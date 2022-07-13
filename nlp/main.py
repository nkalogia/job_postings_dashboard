from fastapi import FastAPI, Body
from celery.result import AsyncResult
from starlette.responses import JSONResponse

from skills import predict
from models import Text, Task, Prediction

app = FastAPI()

@app.post('/skills', status_code=202)
def run_skill_task(payload=Body(...)):
    """Schedules skill prediction and returns retrieval id"""
    keys = {'html', 'plain'}
    data = {k:payload.get(k, None) for k in keys}
    # print(data)
    task = predict.delay(data)
    return JSONResponse({'task_id': task.id, 'status': 'Processing'})

# @app.post('/skills', response_model=Task, status_code=202)
# async def skills(text: Text):
#     task = predict.delay(text.data)
#     print(type(task.id))
#     return {'task_id': task.id, 'status': 'Processing'}

@app.get('/skills/{task_id}', status_code=200)
async def get_skills(task_id):
    """Get the skills list for a specific id"""
    task = AsyncResult(task_id)
    if not task.ready():
        return JSONResponse(status_code=202, content={'task_id': str(task_id), 'status': 'Processing'})
    result = task.get()
    return JSONResponse({'task_id': task_id, 'status': 'Success', 'skills': result})
    # return {'task_id': str(task_id), 'status': 'Success', 'skills': result}
