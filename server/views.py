from server.wsgi import create_app, create_redis_connection
from flask import request, jsonify
import base64
from rq import Queue
from io import BytesIO
from PIL import Image

app = create_app()
r = create_redis_connection()
q = Queue(connection=r)


def resize_image(img, size):
    img = base64.b64decode(img)
    original_image = Image.open(BytesIO(img))
    resized_image = original_image.resize(size)
    return base64.b64encode(resized_image.tobytes())


def upload_and_resize_image(not_resized_img_index: int, new_resized_img_id, size) -> str:
    base64_img = r.hget('not_resized_images', not_resized_img_index)
    resized_img = resize_image(base64_img, size)
    print("save new photo")
    r.hset('resized_images', new_resized_img_id, resized_img)

    url = '/images/{}'.format(not_resized_img_index)
    return url


def save_image(image) -> int:
    base64_img = base64.b64encode(image.read())
    id = r.incr('id_not_resized_images')
    r.hset('not_resized_images', id, base64_img)
    return id


@app.route('/scale_image', methods=["POST"])
def index():
    image_file = request.files['img']
    app.logger.info(2)

    app.logger.info(request.form['width'])
    width = int(request.form['width'])
    height = int(request.form['height'])
    size = (width, height)
    img_index = save_image(image_file)

    id = r.incr('id_resized_images')
    q.enqueue(upload_and_resize_image, img_index, id, size)

    url = '/images/{}'.format(id)
    return url


@app.route('/images/<img_index>')
def get_img(img_index):
    image = r.hget('resized_images', img_index)
    return jsonify({"img": image}), 200