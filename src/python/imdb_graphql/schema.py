import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from sqlalchemy import func, desc

from .models import (
    Title as TitleModel,
    Movie as MovieModel,
    Series as SeriesModel,
    Episode as EpisodeModel,
    EpisodeInfo as EpisodeInfoModel,
    Rating as RatingModel,
    Name as NameModel,
    TitleType as TitleTypeEnum
)

TitleType = graphene.Enum.from_enum(TitleTypeEnum)

class Rating(SQLAlchemyObjectType):
    class Meta:
        model = RatingModel
        interfaces = (graphene.relay.Node, )

    imdbID = graphene.String()
    averageRating = graphene.Float()
    numVotes = graphene.Int()


class Title(graphene.Interface):
    imdbID = graphene.String()
    titleType = graphene.String()
    primaryTitle = graphene.String()
    originalTitle = graphene.String()
    isAdult = graphene.Boolean()
    startYear = graphene.Int()
    endYear = graphene.Int()
    runtime = graphene.Int()
    genres = graphene.String()
    averageRating = graphene.Float()
    numVotes = graphene.Int()

exclude_fields = ('titleSearchCol', '_type', )


class Movie(SQLAlchemyObjectType):
    class Meta:
        model = MovieModel
        interfaces = (Title, )
        exclude_fields = exclude_fields


class Episode(SQLAlchemyObjectType):
    class Meta:
        model = EpisodeModel
        interfaces = (Title, )
        exclude_fields = exclude_fields

    seasonNumber = graphene.Int()
    episodeNumber = graphene.Int()
    series = graphene.Field(lambda: Series)


class Series(SQLAlchemyObjectType):
    class Meta:
        model = SeriesModel
        interfaces = (Title, )
        exclude_fields = exclude_fields

    totalSeasons = graphene.Int()
    episodes = graphene.Field(
        graphene.List(Episode),
        season=graphene.List(graphene.Int)
    )

    def resolve_episodes(self, info, **args):
        query = (
            Episode
            .get_query(info)
            .join(EpisodeModel.info)
            .filter_by(seriesID=self.imdbID)
        )
        query = (
            query.filter(EpisodeInfoModel.seasonNumber.in_(args['season']))
            if 'season' in args else query
        )
        query = (
            query.order_by(
                EpisodeInfoModel.seasonNumber,
                EpisodeInfoModel.episodeNumber
            )
            if 'season' in args and len(args['season']) > 1
            else query.order_by(EpisodeInfoModel.episodeNumber)
        )
        return query

    def resolve_totalSeasons(self, info):
        return(
            EpisodeInfoModel
            .query
            .with_entities(EpisodeInfoModel.seasonNumber)
            .filter_by(seriesID=self.imdbID)
            .group_by(EpisodeInfoModel.seasonNumber)
            .count()
        )

class Name(SQLAlchemyObjectType):
    class Meta:
        model = NameModel
        interfaces = (graphene.relay.Node, )
        exclude_fields = ('id', )
    
    imdbID = graphene.String()
    birthYear = graphene.Int()
    deathYear = graphene.Int()
    primaryName = graphene.String()
    primaryProfession = graphene.String()
    knownForTitles = graphene.List(Title)

    def resolve_knownForTitles(self, info):
        query = (
            TitleModel
            .query
            .filter(TitleModel.imdbID.in_(self.knownForTitles.split(',')))
        ) if self.knownForTitles is not None else None

        return query


class Query(graphene.ObjectType):
    title = graphene.Field(Title, imdbID=graphene.String(required=True))
    movie = graphene.Field(Movie, imdbID=graphene.String(required=True))
    series = graphene.Field(Series, imdbID=graphene.String(required=True))
    episode = graphene.Field(Episode, imdbID=graphene.String(required=True))
    titleSearch = graphene.Field(
        graphene.List(Title),
        title=graphene.String(required=True),
        types=graphene.List(TitleType),
        result=graphene.Int(default_value=5)
    )
    name = graphene.Field(Name, imdbID=graphene.String(required=True))
    rating = graphene.Field(Rating, imdbID=graphene.String(required=True))
    nameSearch = graphene.Field(
        graphene.List(Name),
        name=graphene.String(required=True),
        result=graphene.Int(default_value=10)
    )

    def resolve_title(self, info, imdbID):
        return TitleModel.query.filter_by(imdbID=imdbID).first()

    def resolve_movie(self, info, imdbID):
        return Movie.get_query(info).filter_by(imdbID=imdbID).first()

    def resolve_series(self, info, imdbID):
        return Series.get_query(info).filter_by(imdbID=imdbID).first()

    def resolve_episode(self, info, imdbID):
        return Episode.get_query(info).filter_by(imdbID=imdbID).first()

    def resolve_titleSearch(self, info, title, types=None, result=None):
        tsquery = func.to_tsquery(f'\'{title}\'')
        query = (
            TitleModel
            .query
            .filter(TitleModel.titleSearchCol.op('@@')(tsquery))
        )
        query = (
            query.filter(TitleModel._type.in_(types))
            if types is not None else query
        )
        query = (
            query
            .join(TitleModel.rating)
            .order_by(
                desc(RatingModel.numVotes >= 1000),
                desc(TitleModel.primaryTitle.ilike(title)),
                desc(RatingModel.numVotes),
                desc(func.ts_rank_cd(TitleModel.titleSearchCol, tsquery, 1))
            )
            .limit(result)
        )
        return query
    
    def resolve_name(self, info, imdbID):
        return NameModel.query.filter_by(imdbID=imdbID).first()

    def resolve_rating(self, info, imdbID):
        return RatingModel.query.filter_by(imdbID=imdbID).first()

    def resolve_nameSearch(self, info, name, result=None):
        query = (
            NameModel
            .query
            .filter(NameModel.primaryName.ilike(f'%{name}%'))
            .order_by(
                NameModel.primaryName,
                NameModel.birthYear
            )
            .limit(result)
        )
        return query


schema = graphene.Schema(query=Query, types=[Movie, Series, Episode, Name])
