# Import das bibliotecas necessárias
import boto3
import imghdr
from PIL import Image
from io import BytesIO
import logging

logger = logging.getLogger()
logger.setLevel(logging.getLevelName('INFO'))

# Instanciando o client S3
s3 = boto3.client('s3')

def lambda_handler(event, context):
    logger.info("Iniciando execução...")

    # Obter o nome do bucket e a chave do objeto (imagem) enviado
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Obter a imagem do bucket do Amazon S3
    response = s3.get_object(Bucket=bucket, Key=key)
    image_body = response['Body'].read()
    
    # Verificar se o objeto é uma imagem
    logger.info("Checando se o objeto é uma imagem...")
    image_type = imghdr.what(None, h=image_body)
    if not image_type:
        logger.error("O objeto não é uma imagem válida!")
        return {
            'statusCode': 400,
            'body': 'O objeto não é uma imagem válida.'
        }
    else:
      logger.info("O objeto é uma imagem válida!")
    
    # Redimensionar a imagem
    logger.info("Redimensionando a imagem...")
    image = Image.open(BytesIO(image_body))
    resized_image = image.resize((150, 150))  # Redimensionar para 150x150 pixels
    
    # Salvar a imagem redimensionada no bucket no Amazon S3
    output_bucket = "bucket-processamento-imagens"
    output_file_name = key.split("/")[-1]
    output_key = f"processadas/processed_{output_file_name}"
    output_buffer = BytesIO()
    resized_image.save(output_buffer, format=image.format)
    output_buffer.seek(0)
    logger.info(f"Salvando imagem redimensionada em S3://{output_bucket}/{output_key}")
    s3.put_object(Bucket=output_bucket, Key=output_key, Body=output_buffer)
    
    return {
        'statusCode': 200,
        'body': 'Imagem redimensionada com sucesso!'
    }