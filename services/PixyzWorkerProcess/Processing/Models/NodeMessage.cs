using ServiceUtilities.Process.RandomAccessFile;
using Newtonsoft.Json;

namespace PixyzWorkerProcess.Processing.Models
{
    public class NodeMessage
    {
        [JsonProperty("model_id")]
        public ulong ModelId { get; set; }
        
        [JsonProperty("errors")]
        public string Errors { get; set; }

        [JsonProperty("hierarchyNode")]
        public HierarchyNode HierarchyNode { get; set; }

        [JsonProperty("metadataNode")]
        public MetadataNode MetadataNode { get; set; }

        [JsonProperty("geometryNode")]
        public LodMessage GeometryNode { get; set; }

        [JsonProperty("done")]
        public bool Done { get; set; }

        [JsonProperty("messageCount")]
        public int MessageCount { get; set; }

    }
}
