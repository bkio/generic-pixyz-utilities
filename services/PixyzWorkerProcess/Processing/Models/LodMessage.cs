using Newtonsoft.Json;
using ServiceUtilities.Process.RandomAccessFile;
using System;
using System.Collections.Generic;
using System.Text;

namespace PixyzWorkerProcess.Processing.Models
{
    public class LodMessage:GeometryNode
    {
        public const string LODS_PROPERTY = "lodNumber";
        [JsonProperty(LODS_PROPERTY)]
        public int LodNumber { get; set; }
    }
}
