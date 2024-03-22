from fastapi import APIRouter, Depends

from dependencies.authenticate import authenticate
from .admin import adminRouter
from .user import userRouter
from .auth import authRouter
from .action import actionRouter
apiRouter = APIRouter()

apiRouter.include_router(router=adminRouter, prefix="/admin", tags=["Admin Routes"])
apiRouter.include_router(router=userRouter, prefix="/user",dependencies=[Depends(authenticate)], tags=["User Routes"])
apiRouter.include_router(router=authRouter, prefix="/auth", tags=["Authentication Routes"])
apiRouter.include_router(router=actionRouter, prefix="/action" , dependencies=[Depends(authenticate)], tags=["Actions"])