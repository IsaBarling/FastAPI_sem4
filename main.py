from fastapi import FastAPI, BackgroundTasks
import requests
import os
import time
import concurrent.futures
import asyncio
import aiohttp

app = FastAPI()


# Функция для скачивания изображения и сохранения его на диск
def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        image_name = url.split("/")[-1]
        with open(image_name, "wb") as f:
            f.write(response.content)
        return image_name


# Функция для многопроцессорного скачивания
def download_images_multiprocessing(urls):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        image_names = list(executor.map(download_image, urls))
    return image_names


# Функция для асинхронного скачивания
async def download_image_async(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            image_name = url.split("/")[-1]
            image_data = await response.read()
            with open(image_name, "wb") as f:
                f.write(image_data)
            return image_name


async def download_images_async(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [download_image_async(session, url) for url in urls]
        image_names = await asyncio.gather(*tasks)
    return image_names


@app.get("/download-images/")
async def download_images(urls: list[str], background_tasks: BackgroundTasks):
    start_time = time.time()

    # Многопоточное скачивание
    with concurrent.futures.ThreadPoolExecutor() as executor:
        image_names_threading = list(executor.map(download_image, urls))

    # Многопроцессорное скачивание
    image_names_multiprocessing = download_images_multiprocessing(urls)

    # Асинхронное скачивание
    image_names_async = await download_images_async(urls)

    end_time = time.time()
    total_time = end_time - start_time

    # Удаление временно созданных файлов
    all_image_names = image_names_threading + image_names_multiprocessing + image_names_async
    for image_name in all_image_names:
        if os.path.exists(image_name):
            os.remove(image_name)

    return {
        "message": f"Downloading {len(urls)} images using different approaches. Total time: {total_time:.2f} seconds"
    }
