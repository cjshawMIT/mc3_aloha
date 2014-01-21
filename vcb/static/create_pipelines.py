Curl commands for creating Amazon S3 pipeline
From the Dev Guide:
http://s3.amazonaws.com/awsdocs/elastictranscoder/latest/elastictranscoder-dg.pdf

curl -X POST -H "application/json" -d '{"key":"value"}' URL

My JSON:
{
  'POST': '/2012-09-25/pipelines'
  'HOST': 'elastictranscoder.us-east-1.amazonaws.com:443',
  
}