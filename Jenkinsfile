pipeline {
    agent any

    stages {
        stage('Descargar el repositorio') {
            steps {
                // Clona tu repositorio privado desde Git utilizando la credencial definida en Jenkins
                checkout([$class: 'GitSCM', branches: [[name: 'main']], userRemoteConfigs: [[url: 'https://MartoBigOdi:odilbertito1987@github.com/MartoBigOdi/proxies-finder.git']]])
            }
        }

        stage('Construir y Levantar la Aplicación') {
            steps {
                // Ejecuta el comando para construir e iniciar la aplicación con Docker Compose en Windows
                bat 'docker-compose up -d --build'
            }
        }

        stage('Enviar correo') {
            steps {
                // Envia un correo electrónico con resultados de la ejecución
                mail to: 'martin.vasconcelo@gmail.com',
                     subject: 'Ejecución exitosa de Jenkins',
                     body: 'La ejecución de Jenkins se ha completado correctamente.'
            }
        }
    }
}
