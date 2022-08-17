from flask import Blueprint
from flask_restful import Api
from resources.UserResource import UserResource
from resources.backtest_resource import BacktestResource
from resources.daily_selection import DailySelectionResource
from resources.deploy_strategy_resource import DeployStrategyResource
from resources.instrument_resource import InstrumentsResource
from resources.operator_resource import OperatorResource, OperatorsResource
from resources.screener_resource import ScreenerResource, ScreenersResource
from resources.strategy_resource import StrategyResource, StrategiesResource
from resources.technical_resource import TechnicalResource, TechnicalsResource
from resources.authentication_resource import AuthenticationResource
from resources.seed_resource import SeedResource
from resources.derivative_analysis_resource import DerivativeAnalysisResource, DetailedDerivativeAnalysisResource

api_bp = Blueprint('api', __name__)

@api_bp.route('/')
def index():
 return render_template('index.html')

api = Api(api_bp)

# Route
api.add_resource(UserResource, '/user')

api.add_resource(StrategyResource, '/strategy', '/strategy/<string:id>')

api.add_resource(StrategiesResource, '/strategies')

api.add_resource(ScreenerResource, '/screener', '/screener/<string:id>')

api.add_resource(ScreenersResource, '/screeners')

api.add_resource(TechnicalResource, '/technical', '/technical/<string:_id>')

api.add_resource(AuthenticationResource, '/authentication')

api.add_resource(OperatorResource, '/operator', '/operator/<string:_id>')

api.add_resource(TechnicalsResource, '/technicals')

api.add_resource(OperatorsResource, '/operators')

api.add_resource(InstrumentsResource, '/instruments')

api.add_resource(DeployStrategyResource, '/deploy')

api.add_resource(BacktestResource, '/backtest')

api.add_resource(DerivativeAnalysisResource, '/derivativeAnalysisResult')

api.add_resource(SeedResource, '/seed')

api.add_resource(DetailedDerivativeAnalysisResource, '/detailDerivativeAnalysisResult/<string:stock>')

api.add_resource(DailySelectionResource, '/dailySelection', '/dailySelection/<string:id>')
