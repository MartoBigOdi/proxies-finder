FROM python:3.9

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de tu aplicación al contenedor
COPY . /app

# Instala las dependencias del proyecto
RUN pip install -r requirements.txt
RUN apt-get update && \
    apt-get install -yq libnss3 libglib2.0-0 libx11-6 && \
    apt-get clean

# Instalamos playwright y continuamos incluso si falla
RUN playwright install || true
RUN playwright install-deps || true

# Define el comando para ejecutar la aplicación
CMD ["python", "main.py"]