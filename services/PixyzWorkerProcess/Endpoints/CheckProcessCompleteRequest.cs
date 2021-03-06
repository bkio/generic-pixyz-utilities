﻿using BWebServiceUtilities;
using PixyzWorkerProcess.Processing;
using ServiceUtilities.All;
using System;
using System.Collections.Generic;
using System.Net;
using System.Text;

namespace PixyzWorkerProcess.Endpoints
{
    class CheckProcessCompleteRequest: BppWebServiceBase
    {
        protected override BWebServiceResponse OnRequestPP(HttpListenerContext _Context, Action<string> _ErrorMessageAction = null)
        {
            GetTracingService()?.On_FromServiceToService_Received(_Context, _ErrorMessageAction);

            var Result = OnRequest_Internal(_Context, _ErrorMessageAction);

            GetTracingService()?.On_FromServiceToService_Sent(_Context, _ErrorMessageAction);

            return Result;
        }

        private BWebServiceResponse OnRequest_Internal(HttpListenerContext _Context, Action<string> _ErrorMessageAction)
        {
            try
            {
                if (BatchProcessingService.Instance.CheckProcessComplete())
                {
                    return BWebResponse.StatusOK(BatchProcessingService.Instance.State);
                }
                else
                {
                    return BWebResponse.NotAcceptable("Queue not ready");
                }
            }
            catch (Exception ex)
            {
                _ErrorMessageAction?.Invoke($"{ex.Message}\n{ex.StackTrace}");
                return BWebResponse.InternalError("Failed to get state");
            }
        }
    }
}
