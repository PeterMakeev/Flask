import pydantic
from typing import Union
from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy import Column, Integer, String, DateTime, create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

app = Flask('app')

class HTTPError(Exception):
    def __init__(self, status_code: int, message: Union[str, list, dict]):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HTTPError)
def error_handler(error: HTTPError):
    response = jsonify({'status': 'error', 'message': error.message})
    response.status_code = error.status_code
    return response


DSN = 'postgresql://app:1234@127.0.0.1:5431/ads'

engine = create_engine(DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class MarketModel(Base):
    __tablename__ = 'market'

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    creation_time = Column(DateTime, server_default=func.now())
    owner = Column(String(255), index=True, nullable=False)


Base.metadata.create_all(engine)

class CreateMarketSchema(pydantic.BaseModel):
    title: str
    description: str
    owner: str

    @pydantic.validator('title')
    def check_title(cls, value: str):
        if len(value) > 32:
            raise ValueError('Title mast be less 32 chars')
        return value


def validate(data_to_validate: dict, validation_class):
    try:
        return validation_class(**data_to_validate).dict()
    except pydantic.ValidationError as err:
        raise HTTPError(400, err.errors())

def get_by_id(item_id: int, orm_model, session):
    orm_item = session.query(orm_model).get(item_id)
    if orm_item is None:
        raise HTTPError(404, 'item not found')
    return orm_item



class MarketView(MethodView):
    def get(self, ad_id: int):
        with Session() as session:
            ad = get_by_id(ad_id, MarketModel, session)
            return jsonify({
                'title': ad.title,
                'creation_time': ad.creation_time.isoformat(),
                'description': ad.description,
                'owner': ad.owner,
            })

    def post(self):
        json_data = request.json
        print(json_data)
        with Session() as session:
            try:
                ads = MarketModel(**validate(json_data, CreateMarketSchema))
                session.add(ads)
                session.commit()
            except pydantic.ValidationError:
                raise HTTPError(400, 'Error')
            return jsonify({
                'status': 'ok',
                'id': ads.id,
                'title': ads.title,
                'description': ads.description,
                'owner': ads.owner,
            })

    def delete(self, ad_id: int):
        with Session() as session:
            ad = get_by_id(ad_id, MarketModel, session)
            session.delete(ad)
            session.commit()
            return jsonify({
                'status': 'success'
            })


app.add_url_rule('/market/<int:ad_id>/', view_func=MarketView.as_view('ads_get'), methods=['DELETE', 'GET'])
app.add_url_rule('/market/', view_func=MarketView.as_view('ads_create'), methods=['POST'])

app.run()