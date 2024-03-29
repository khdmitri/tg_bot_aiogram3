from aiogram import Router

from handlers.blog import blog


def prepare_router() -> Router:
    blog_router = Router()

    blog_router.channel_post.register(blog.check_new_post)

    return blog_router
