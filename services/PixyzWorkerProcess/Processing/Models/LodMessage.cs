using Newtonsoft.Json;
using ServiceUtilities.Process.RandomAccessFile;

namespace PixyzWorkerProcess.Processing.Models
{
    public class LodMessage : GeometryNode
    {
        public const string LOD_NUMBER_PROPERTY = "lodNumber";
        [JsonProperty(LOD_NUMBER_PROPERTY)]
        public int LodNumber { get; set; }
    }
}
