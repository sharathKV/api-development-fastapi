import json
from sqlalchemy.orm import Session
from typing import Optional
from app import oauth2
from .. import models, schemas
from fastapi import status, HTTPException, Depends, APIRouter, Response
from ..database import get_db
from typing import List
from sqlalchemy import func

router = APIRouter(prefix="/posts", tags=['Posts'])

@router.get("/", response_model=List[schemas.PostsWithVotes])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # cursor.execute('''SELECT * FROM posts''')
    # posts = cursor.fetchall()
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    results = db.query(models.Post, func.count(models.Votes.post_id).label("votes")) \
                .join(models.Votes, models.Votes.post_id == models.Post.id, isouter=True) \
                .group_by(models.Post.id)  \
                .filter(models.Post.title.contains(search)) \
                .limit(limit) \
                .offset(skip) \
                .all()
                
    data = [{'Post': k, 'votes': v} for k, v in results]  
    return data

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute('''INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *''', (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/{id}", response_model=schemas.PostsWithVotes)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute('''SELECT * FROM posts WHERE id = %s''', (str(id)))
    # some_post = cursor.fetchone()
    # one_post_query = db.query(models.Post).filter(models.Post.id == id)
    # one_post = one_post_query.first()
    post = db.query(models.Post, func.count(models.Votes.post_id).label("votes")) \
             .join(models.Votes, models.Votes.post_id == models.Post.id, isouter=True) \
             .group_by(models.Post.id) \
             .filter(models.Post.id == id) \
             .first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=F"post with id: {id} was not found")

    data = {'Post': post[0], 'votes': post[1]}

    return data

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute('''DELETE FROM posts WHERE id = %s returning *''', (str(id)))
    # deleted_post = cursor.fetchone()
    
    deleted_post_query = db.query(models.Post).filter(models.Post.id == id)
    deleted_post = deleted_post_query.first()
    
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    
    # conn.commit()
    if deleted_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not authorized to perform requested action")
    
    deleted_post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute('''UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *''', (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="not authorized to perform requested action")
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    # conn.commit()
    return post_query.first()