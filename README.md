# common_utils
This repo contains different general purpose functions that is used across different projects


Env variables that the functions expect: 

- GOOGLE_CLOUD_PROJECT: The project id of the GCP project that you are running the function in. THis is set by default if you are running the code in a GCP env. 
- ENV: Can be either dev or prod and determines the behavior of the log.


Other info: 

When running the code with ENV set to prod make sure that you have GOOGLE_APPLICATION_CREDENTIALS env variable defined or any of the other GCP authentication methods avaible with a service account with permission to write logs. 