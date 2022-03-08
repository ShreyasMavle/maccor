FROM public.ecr.aws/lambda/python:3.8
RUN /var/lang/bin/python3.8 -m pip install --upgrade pip

# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}

# Instead of installing the function's dependencies using file requirements.txt
# using source code changed locally
COPY requirements.txt  .
ADD dependencies "${LAMBDA_TASK_ROOT}"


# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.handler" ]