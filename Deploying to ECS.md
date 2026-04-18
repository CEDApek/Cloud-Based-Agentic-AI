# mini-agentic-ai aws deployment report

## 1. objective

The goal was to take a local containerized FastAPI application and deploy it to AWS so it could run as a public web service. In this deployment flow, the app code was packaged into a Docker image, stored in Amazon ECR, and then deployed through Amazon ECS Express Mode, which automatically provisions supporting infrastructure such as the load balancer, security groups, target groups, auto-scaling policy, and logging.

## 2. local application preparation

Before using AWS, I first made sure the application worked locally. The project already had a `Dockerfile`, a FastAPI app, and a health-check endpoint, so it was suitable for container deployment. The important idea here is that ECS does not upload raw Python files directly; instead, it runs a **container image**, so the application must first be packaged with Docker. AWS’s ECS getting started material also frames container deployment around building an image first and then uploading it to ECR.

## 3. aws cli configuration

I configured AWS CLI locally so my terminal could authenticate to my AWS account and know which Region to use by default. Running `aws configure` prompts for the AWS access key ID, secret access key, default Region, and output format, and stores the configuration under the local AWS config files. This step is what allows later commands like ECR and ECS operations to work from the terminal.

Example:

aws configure

I set:

- access key
- secret key
- default region, for example `ap-southeast-1`
- output format, for example `json`

## 4. create a private ecr repository

Next, I created an Amazon ECR private repository. ECR is the image registry that stores Docker images so AWS services like ECS can pull and run them later. This is a necessary step because ECS Express Mode expects a container image as one of its main inputs.

Example:

aws ecr create-repository \  
  --repository-name mini-agentic-ai \  
  --region ap-southeast-1

## 5. authenticate docker to ecr

After creating the repository, I authenticated Docker to the ECR registry. AWS documents this as getting a login password from ECR for a specific Region and piping it into `docker login`. The Region used here must match the Region of the ECR registry.

Example:

aws ecr get-login-password --region ap-southeast-1 | \  
docker login --username AWS --password-stdin 391254865159.dkr.ecr.ap-southeast-1.amazonaws.com

## 6. build the docker image locally

Then I built the application into a Docker image on my own machine. This converts the project from source code into a portable container artifact that can be run consistently in AWS.

Example:

docker build -t mini-agentic-ai .

## 7. tag and push the image to ecr

After building the image, I tagged it with the ECR repository URI and pushed it to the repository. This is the actual “upload” step for the application artifact. What gets uploaded to the cloud here is not the raw project folder, but the built Docker image. AWS’s ECR documentation describes the standard flow as authenticate, tag the image with the repository URI, and then `docker push` it.

Example:

docker tag mini-agentic-ai:latest \  
  391254865159.dkr.ecr.ap-southeast-1.amazonaws.com/mini-agentic-ai:latest  

docker push \  
  391254865159.dkr.ecr.ap-southeast-1.amazonaws.com/mini-agentic-ai:latest

## 8. create the iam roles required by ecs express mode

ECS Express Mode requires two IAM roles: a **task execution role** and an **infrastructure role**. AWS documents these as core inputs for Express Mode, along with the container image. The task execution role allows ECS tasks to perform runtime operations such as pulling images and writing logs, while the infrastructure role lets ECS manage supporting AWS resources on my behalf.

First, I created the execution role and attached the standard ECS task execution policy. Then I created the infrastructure role with the trust relationship needed for ECS Express Mode and attached the infrastructure policy required for managed resources. This was necessary so ECS could create and manage the load balancer, target groups, security groups, and monitoring resources automatically.

## 9. create the ecs express mode service

Once the image existed in ECR and the two IAM roles were ready, I created the ECS Express Mode service. AWS describes Express Mode as a simplified deployment model for containerized web applications that needs only a container image, a task execution role, and an infrastructure role to get started. When the service is created, ECS automatically provisions managed infrastructure such as Application Load Balancers, target groups, security groups, and auto-scaling policies.

Example:

aws ecs create-express-gateway-service \  
  --service-name mini-agentic-ai \  
  --execution-role-arn arn:aws:iam::391254865159:role/ecsTaskExecutionRole \  
  --infrastructure-role-arn arn:aws:iam::391254865159:role/ecsInfrastructureRoleForExpressServices \  
  --primary-container '{"image":"391254865159.dkr.ecr.ap-southeast-1.amazonaws.com/mini-agentic-ai:latest","containerPort":8000}' \  
  --health-check-path "/status" \  
  --monitor-resources \  
  --region ap-southeast-1

In this step:

- `image` pointed to the pushed ECR image
- `containerPort` matched the app’s listening port
- `health-check-path` matched the FastAPI health endpoint
- `--monitor-resources` enabled the managed observability resources AWS creates for the service.

## 10. monitor deployment status

After submitting the ECS command, AWS showed a live deployment monitor. This interface reflected the creation and status of the managed resources. AWS’s Express service APIs describe this service state as including current status, managed infrastructure, service revisions, ingress endpoints, and resource status such as load balancers and auto-scaling policies.

A successful deployment eventually reached:

- service steady state
- successful deployment
- active supporting resources

That meant the container was running and the ECS service was healthy. In practice, this also meant AWS had already created the ECS service, task definition, target groups, ALB-related resources, and logging resources.

## 11. understand what aws created automatically

A useful lesson from this deployment is that ECS Express Mode did much more than “run a container.” It automatically created and managed the networking and supporting infrastructure around the app. AWS explicitly states that Express Mode provisions traffic distribution, health monitoring, network access control, and capacity management for the application.

So the real deployed architecture was roughly:

internet  
  ↓  
managed https endpoint / load balancer  
  ↓  
ecs express service  
  ↓  
fargate task running my container  
  ↓  
cloudwatch logs and monitoring

This is why cloud deployment is more than just “putting code on a server.” It includes orchestration, networking, availability, and observability.

## 12. get the real public endpoint

At first, querying the raw ALB DNS name returned a `404 Not Found`. The reason was that the ALB listener had a default fixed 404 action, and the actual service routing depended on the Express-managed endpoint and host-based routing rather than directly using the raw ALB hostname. AWS documents Express service description as returning ingress paths with endpoints, which is where the correct public hostname comes from. ALB listener rules also support host-header based matching, which explains why the raw ALB hostname did not behave like the final public application URL.

So I used:

aws ecs describe-express-gateway-service \  
  --cluster default \  
  --service mini-agentic-ai \  
  --region ap-southeast-1

This returned the actual `*.ecs.ap-southeast-1.on.aws` endpoint, which was the correct public address for the application.

## 13. test the deployed application

After finding the actual Express endpoint, I tested the service over HTTPS. I verified the health endpoint and then tested the application’s main API endpoint. This confirmed that the image was pulled correctly from ECR, the ECS service was running, the target was healthy, and the application was reachable from the internet through the managed ingress.

Example:

curl https://YOUR-EXPRESS-ENDPOINT/status

and then:

curl -X POST https://YOUR-EXPRESS-ENDPOINT/run \  
  -H "Content-Type: application/json" \  
  -d '{"goal":"write a note: hello from aws, then show notes"}'

## 14. check status later in console

To check the service later in the AWS Console, I can open Amazon ECS, go to the cluster, and inspect the service and its tasks. AWS also provides service description commands and Express service description commands that return status, service revisions, and managed infrastructure details. For logs and observability, CloudWatch log groups were created automatically as part of the monitored resources.

Useful CLI checks:

aws ecs describe-services \  
  --cluster default \  
  --services mini-agentic-ai \  
  --region ap-southeast-1

aws ecs describe-express-gateway-service \  
  --cluster default \  
  --service mini-agentic-ai \  
  --region ap-southeast-1

## 15. what “always on” means

The service remains running as long as the ECS service exists and the desired task count is maintained. In other words, AWS keeps the service alive for me rather than me manually starting it each time. However, this also means the service continues consuming billable AWS resources until I stop or delete it. ECS services are designed to maintain the desired number of tasks, and the supporting Express infrastructure includes capacity management and health monitoring.

## 16. limitation noticed in this project

One important architectural limitation is that my current application stores notes and todo data as local files inside the container. This is acceptable for a learning deployment, but it is not durable cloud storage. If the container is replaced, redeployed, or scaled, local file data can be lost or become inconsistent across tasks. A more cloud-native version would move persistent state to a managed storage service rather than keeping it inside the container filesystem. This is an inference from how containerized ECS services work and from the fact that Express Mode focuses on stateless web application deployment infrastructure rather than persistent local disk as a shared application data layer.

## 17. short summary

In summary, the deployment flow was:

1. prepare the local app and Dockerfile
2. configure AWS CLI credentials and Region
3. create an ECR repository
4. log Docker into ECR
5. build the Docker image locally
6. tag and push the image to ECR
7. create the IAM roles needed by ECS Express Mode
8. create the ECS Express service using the ECR image
9. wait for AWS to provision the managed infrastructure
10. retrieve the correct Express endpoint
11. test the public application over HTTPS.





<br>

****

#### Mini Documentation

![](/home/ceda/Pictures/Screenshots/Screenshot_20260418_184318.png)

**curl test :**

```bash
curl -vk https://mi-b1d18bd040a9479f9cc90b2cfb6d0118.ecs.ap-southeast-1.on.aws/status
```

```bash
curl -vk -X POST https://mi-b1d18bd040a9479f9cc90b2cfb6d0118.ecs.ap-southeast-1.on.aws/run \
  -H "Content-Type: application/json" \
  -d '{"goal":"write a note: hello from aws, then show notes"}'
```

```bash
curl -vk https://ecs-express-gateway-alb-60342a55-1900026863.ap-southeast-1.elb.amazonaws.com/status \
  -H 'Host: mi-b1d18bd040a9479f9cc90b2cfb6d0118.ecs.ap-southeast-1.on.aws'
```

### Within ECS (aws console)

![](/home/ceda/Pictures/Screenshots/Screenshot_20260418_190514.png)
