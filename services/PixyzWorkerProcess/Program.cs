using BCloudServiceUtilities;
using BCloudServiceUtilities.PubSubServices;
using BServiceUtilities;
using BWebServiceUtilities;
using ServiceUtilities;
using PixyzWorkerProcess.Endpoints;
using PixyzWorkerProcess.Processing;
using System;
using System.Collections.Generic;
using System.Threading;

namespace PixyzWorkerProcess
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Initializing the service...");

            // In case of a cloud component dependency or environment variable is added/removed;

            /*
            * Common initialization step
            */
            if (!BServiceInitializer.Initialize(out BServiceInitializer ServInit,
                new string[][]
                {
                    new string[] { "GOOGLE_CLOUD_PROJECT_ID" },
                    new string[] { "GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_PLAIN_CREDENTIALS" },

                    new string[] { "DEPLOYMENT_BRANCH_NAME" },
                    new string[] { "DEPLOYMENT_BUILD_NUMBER" },

                    new string[] { "REDIS_ENDPOINT" },
                    new string[] { "REDIS_PORT" },
                    new string[] { "REDIS_PASSWORD" },

                    new string[] { "UPLOAD_HIERARCHY_CF" },
                    new string[] { "UPLOAD_HIERARCHY_RAF" },
                    new string[] { "UPLOAD_GEOMETRY_CF" },
                    new string[] { "UPLOAD_GEOMETRY_RAF" },
                    new string[] { "UPLOAD_METADATA_CF" },
                    new string[] { "UPLOAD_METADATA_RAF" },
                    new string[] { "IS_FILE_WRITE" },

                    new string[] { "CAD_PROCESS_NOTIFY_URL" }
                }))
                return;

            bool IsFileWrite = bool.Parse(ServInit.RequiredEnvironmentVariables["IS_FILE_WRITE"]);
            bool bInitSuccess = true;

            if(!IsFileWrite)
            {
                bInitSuccess &= ServInit.WithFileService();
                bInitSuccess &= ServInit.WithTracingService();
            }

            //Wait for redis
            int RetryCount = 0;
            while (true)
            {
                try
                {
                    bInitSuccess &= ServInit.WithMemoryService(true, new BPubSubServiceRedis(ServInit.RequiredEnvironmentVariables["REDIS_ENDPOINT"], int.Parse(ServInit.RequiredEnvironmentVariables["REDIS_PORT"]), ServInit.RequiredEnvironmentVariables["REDIS_PASSWORD"]));
                    break;
                }
                catch (Exception ex)
                {
                    RetryCount++;
                    Thread.Sleep(1000);
                    if (RetryCount >= 30)
                    {
                        break;
                    }
                }
            }

            if (!bInitSuccess) return;

            if(!BatchProcessingService.Initialize(ServInit.MemoryService))
            {
                //Exit with an error code so that health checker can pick up on it and take action
                Environment.Exit(1);
            }

            BatchProcessingService.Instance.SetUploadUrls(
                ServInit.RequiredEnvironmentVariables["UPLOAD_HIERARCHY_CF"],
                ServInit.RequiredEnvironmentVariables["UPLOAD_HIERARCHY_RAF"],
                ServInit.RequiredEnvironmentVariables["UPLOAD_METADATA_CF"],
                ServInit.RequiredEnvironmentVariables["UPLOAD_METADATA_RAF"],
                ServInit.RequiredEnvironmentVariables["UPLOAD_GEOMETRY_CF"],
                ServInit.RequiredEnvironmentVariables["UPLOAD_GEOMETRY_RAF"],
                ServInit.RequiredEnvironmentVariables["CAD_PROCESS_NOTIFY_URL"],
                IsFileWrite);

            BatchProcessingService.Instance.StartProcessingBatchData((Message) => { Console.WriteLine(Message); });


            //if (!IsFileWrite)
            //{
                Resources_DeploymentManager.Get().SetDeploymentBranchNameAndBuildNumber(ServInit.RequiredEnvironmentVariables["DEPLOYMENT_BRANCH_NAME"], ServInit.RequiredEnvironmentVariables["DEPLOYMENT_BUILD_NUMBER"]);

                var WebServiceEndpoints = new List<BWebPrefixStructure>()
            {
                new BWebPrefixStructure(new string[] { "/healthcheck" }, () => new HealthCheckRequest())
            };

                var BWebService = new BWebService(WebServiceEndpoints.ToArray(), ServInit.ServerPort, ServInit.TracingService);

                BWebService.Run((string Message) =>
                {
                    ServInit.LoggingService.WriteLogs(BLoggingServiceMessageUtility.Single(EBLoggingServiceLogType.Info, Message), ServInit.ProgramID, "WebService");
                });
            //}

            Thread.Sleep(Timeout.Infinite);
        }
    }
}
