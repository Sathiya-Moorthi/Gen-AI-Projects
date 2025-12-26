from flask import Blueprint, jsonify, g
from app.models import User
from app.utils.decorators import requires_role

bp = Blueprint('hierarchy', __name__, url_prefix='/hierarchy')

@bp.route('/team', methods=['GET'])
@requires_role('Direct_Manager')
def get_team():
    user_id = g.current_user['user_id']
    
    # Recursive fetch or just direct reports? 
    # Requirement: "recursive or adjacency list model to fetch the organizational tree"
    # "Manager View endpoint returns only the relevant subtree"
    
    def get_subordinates(manager_id):
        subs = User.query.filter_by(manager_id=manager_id).all()
        result = []
        for sub in subs:
            sub_data = sub.to_dict()
            sub_data['reports'] = get_subordinates(sub.id)
            result.append(sub_data)
        return result

    team_tree = get_subordinates(user_id)
    return jsonify(team_tree), 200
