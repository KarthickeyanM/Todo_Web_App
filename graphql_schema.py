import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from models import Todo as TodoModel, session
from app import oidc


class TodoType(SQLAlchemyObjectType):
    class Meta:
        model = TodoModel

class Query(graphene.ObjectType):
    todos = graphene.List(TodoType)

    def resolve_todos(self, info):
        query = TodoType.get_query(info)
        return query.all()

class CreateTodo(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String(required=True)
        time = graphene.DateTime(required=True)
        images = graphene.String()

    todo = graphene.Field(TodoType)

    def mutate(self, info, title, description, time, images=None):
        user_info = oidc.user_getinfo(['roles'])
        if images and 'pro' not in user_info.get('roles', []):
            raise Exception('You need a Pro license to upload images.')
        
        new_todo = TodoModel(
            title=title,
            description=description,
            time=time,
            images=images
        )
        session.add(new_todo)
        session.commit()
        return CreateTodo(todo=new_todo)

class Mutation(graphene.ObjectType):
    create_todo = CreateTodo.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)