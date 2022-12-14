from sqlalchemy.orm import Session
from uuid import uuid4
from sqlalchemy import desc
from fastapi.templating import Jinja2Templates

from . import models, schemas


def create_user(db: Session, user: schemas.RegisterUser):
    db_user = models.User(
        username=user.username,
        password=user.password,
        nickname=user.nickname,
        user_type=user.user_type,
        is_active=True if user.user_type == schemas.UserType.NORMAL.value else False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, username: str, password: str):
    return db.query(models.User).filter(models.User.username == username, models.User.password == password).first()


def get_token(db: Session, token: str):
    return db.query(models.UserLoginToken).filter(models.UserLoginToken.token == token).first()


def login(db: Session, user_id: int):
    db_user_login = db.query(models.UserLoginToken).filter(models.UserLoginToken.user_id == user_id).first()
    if db_user_login:
        return db_user_login.token
    db_user_login = models.UserLoginToken(
        user_id=user_id,
        token=uuid4()
    )
    db.add(db_user_login)
    db.commit()
    db.refresh(db_user_login)
    return db_user_login.token


def is_user(db: Session, token: str):
    user = db.query(models.UserLoginToken).filter(models.UserLoginToken.token == token).first()
    if user:
        return True
    else:
        return False


def check_type(db: Session, user_id: int, type: models.UserType):
    user = db.query(models.User).filter(models.User.id == user_id).one()
    if user.user_type == type:
        return True
    return False


def get_inactive_admins(db: Session):
    admins = db.query(models.User).filter(
        models.User.user_type == models.UserType.ADMIN, models.User.is_active == False).all()
    return admins


def activate_user(db: Session, user_id: int):
    db.query(models.User).filter(models.User.id == user_id).update({models.User.is_active: True})
    db.commit()


def logout(db: Session, user_logout_token: models.UserLoginToken):
    db.delete(user_logout_token)
    db.commit()
    return user_logout_token.token


def videos(db: Session):
    return db.query(models.Video).filter(models.Video.is_active).all()


def comments(db: Session, video_id: int):
    return db.query(models.Comment).filter(models.Comment.video_id == video_id).all()


def likes(db: Session, video_id: int):
    return db.query(models.Like).filter(models.Like.is_like, models.Like.video_id == video_id).all()


def get_like(db: Session, video_id: int, user_id: int):
    return db.query(models.Like).filter(
        models.Like.is_like, models.Like.video_id == video_id, models.Like.user_id == user_id
    ).first()


def dislikes(db: Session, video_id: int):
    return db.query(models.Like).filter(models.Like.is_like != True, models.Like.video_id == video_id).all()


def get_dislike(db: Session, video_id: int, user_id: int):
    return db.query(models.Like).filter(
        models.Like.is_like != True, models.Like.video_id == video_id, models.Like.user_id == user_id
    ).first()


def get_like_or_dislike(db: Session, video_id: int, user_id: int):
    return db.query(models.Like).filter(models.Like.video_id == video_id, models.Like.user_id == user_id).first()


def delete_like(db: Session, like: models.Like):
    db.delete(like)
    db.commit()


def add_comment(db: Session, comment: schemas.Comment, user_id: int):
    db_comment = models.Comment(
        text=comment.text,
        video_id=comment.video_id,
        user_id=user_id,
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def add_new_comment(db: Session, video_id, text, user_id: int):
    db_comment = models.Comment(
        text=text,
        video_id=video_id,
        user_id=user_id,
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def add_like(db: Session, like: schemas.Like, user_id: int):
    db_like = models.Like(
        is_like=like.is_like,
        video_id=like.video_id,
        user_id=user_id,
    )
    db.add(db_like)
    db.commit()
    db.refresh(db_like)
    return db_like


def add_new_like(db: Session, video_id: int, user_id: int):
    db_like = models.Like(
        is_like=True,
        video_id=video_id,
        user_id=user_id,
    )
    db.add(db_like)
    db.commit()
    db.refresh(db_like)
    return db_like


def add_new_dislike(db: Session, video_id: int, user_id: int):
    db_like = models.Like(
        is_like=False,
        video_id=video_id,
        user_id=user_id,
    )
    db.add(db_like)
    db.commit()
    db.refresh(db_like)
    return db_like


templates = Jinja2Templates(directory="services/video")


def get_video(db: Session, video_id: int, request):
    video = db.query(models.Video).filter(models.Video.id == video_id, models.Video.is_active).first()
    if not video:
        return 'no video'
    video_path = video.file_path
    video_id = video.id
    like_count = len(likes(db, video_id))
    dislike_count = len(dislikes(db, video_id))
    comments_list = list(comments(db, video_id))
    print([c.text for c in comments_list])
    return templates.TemplateResponse(
        "page.html",
        {
            "request": request,
            "file_path": video_path,
            "like_count": like_count,
            "dislike_count": dislike_count,
            "comment_list": [c.text for c in comments_list],
            "video_id": video_id
        }
    )


def upload_video(db: Session, video: schemas.UploadVideo):
    db_video = models.Video(
        file_path=video.file_path,
        user_id=video.user_id,
    )
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video


def inactivate_video(db: Session, video_id):
    video = db.query(models.Video).filter(models.Video.id == video_id).one()
    last_video = db.query(models.Video).filter(
        models.Video.user_id == video.user_id
    ).order_by(desc(models.Video.id)).all()
    print(last_video[1].id, last_video[1].is_active)
    if not last_video[1].is_active:
        db.query(models.User).filter(models.User.id == video.user_id).update({models.User.is_active: False})
    db.query(models.Video).filter(models.Video.id == video_id).update({models.Video.is_active: False})
    db.commit()


def create_boss(db: Session):
    user = db.query(models.User).filter(models.User.user_type == models.UserType.BOSS).first()

    if user:
        return
    boss = models.User(
        username='manager',
        password='supreme_manager#2022',
        nickname='boss',
        user_type=models.UserType.BOSS,
        is_active=True
    )
    db.add(boss)
    db.commit()
    db.refresh(boss)


def label_video(db: Session, video_id: int):
    db.query(models.Video).filter(models.Video.id == video_id).update({models.Video.bad_label: True})
    db.commit()
