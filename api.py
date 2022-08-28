from email.policy import HTTP
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import mysql.connector
import time

app = FastAPI()

while True:
    try:
        conn = mysql.connector.connect(host="<THEHOSTNAME>",database="<THEDATABASENAME>", user="<THEUSER>", password="<THEPASSWORD>")
        break
    except Exception as error:
        print(f'Error: {error}')
        time.sleep(3)


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


@app.get("/")
async def root():
    return {"message": "hey! this is the home"}

@app.get("/posts")
def get_posts():
    mycursor = conn.cursor()
    mycursor.execute("SELECT * FROM posts")
    posts = mycursor.fetchall()
    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    mycursor = conn.cursor()
    sql = "INSERT INTO posts (title, content, published) VALUES (%s, %s, %s)"
    val = (post.title, post.content, post.published)
    mycursor.execute(sql, val)
    conn.commit()
    mycursor.execute("SELECT * from posts WHERE id = (SELECT max(id) FROM `posts`);")
    new_post =mycursor.fetchone()
    return {"data": new_post}

@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    mycursor = conn.cursor()
    sql = "SELECT * from posts WHERE id = %s"
    mycursor.execute(sql, [id])
    post =mycursor.fetchone()
    if not post:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'message': f'post with id: {id} was not found'}
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    mycursor = conn.cursor()
    sql = "DELETE from posts WHERE id = %s"
    mycursor.execute(sql, [id])
    conn.commit()
    if mycursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    return {"deleted_post": f"post number {id} has been deleted"}


@app.put('/posts/{id}')
def update_post(id: int, post: Post):
    mycursor = conn.cursor()
    sql = "UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s"
    mycursor.execute(sql, [post.title, post.content, post.published, id])
    conn.commit()
    if mycursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} was not found')
    return {'data': f"post number {id} has been successfully updated"}