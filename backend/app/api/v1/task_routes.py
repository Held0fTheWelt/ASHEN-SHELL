from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.task_executor_service import TaskExecutorService
from app.extensions import limiter
import logging

logger = logging.getLogger(__name__)

task_routes_bp = Blueprint('tasks', __name__)

@task_routes_bp.route('/tasks', methods=['POST'])
@limiter.limit("10 per minute")
@jwt_required()
def create_task():
    """
    REST route for task execution.

    POST /api/v1/tasks
    Body: { task_id, escalation_level, inputs: { prompt, system_prompt? } }
    Auth: @jwt_required()
    Returns: { target_worker, model, output, cost, cost_formatted, tokens_used, latency_ms }
    """
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        escalation_level = data.get('escalation_level')
        inputs = data.get('inputs')

        if not task_id:
            return jsonify({'error': 'task_id is required'}), 400

        task_executor = TaskExecutorService()  # Instantiate TaskExecutorService here
        result = task_executor.execute_task(task_id, escalation_level, inputs)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error executing task: {e}")
        return jsonify({'error': 'Failed to execute task'}), 500
