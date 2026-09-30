import test from "node:test";
import assert from "node:assert/strict";
import {extractGoogleSources,extractAwsSources,aiSourceParcel} from "../core/ai_source_metadata.mjs";

const QUESTION="I want to go fishing in May for salmon within 200 kilometers of Perth on the beach. What is the best bait?";

test("Google grounding metadata becomes source-only parcel",()=>{
  const response={
    candidates:[{
      content:{parts:[{text:"Use marshmallows. This answer must never enter evidence."}]},
      groundingMetadata:{
        groundingChunks:[
          {web:{uri:"https://example.com/fishing",title:"Fishing source"}},
          {web:{uri:"https://example.com/fishing#dup",title:"Duplicate"}}
        ]
      }
    }]
  };
  const parcel=aiSourceParcel("google",QUESTION,response);
  assert.equal(parcel.ok,true);
  assert.equal(parcel.source_count,1);
  assert.equal(parcel.sources[0].url,"https://example.com/fishing");
  assert.equal(JSON.stringify(parcel).includes("marshmallows"),false);
});

test("Google Interactions url_citation shape is supported",()=>{
  const response={steps:[{type:"model_output",content:[{type:"text",text:"ignored",annotations:[
    {type:"url_citation",url:"https://example.org/a",title:"A"}
  ]}]}]};
  assert.deepEqual(extractGoogleSources(response).map(x=>x.url),["https://example.org/a"]);
});

test("AWS Bedrock url_citation annotations become source-only parcel",()=>{
  const response={output:[{type:"message",content:[{type:"output_text",text:"ignored answer",annotations:[
    {type:"url_citation",url:"https://example.net/b",title:"B",start_index:0,end_index:7}
  ]}]}]};
  const parcel=aiSourceParcel("aws",QUESTION,response);
  assert.equal(parcel.ok,true);
  assert.deepEqual(extractAwsSources(response).map(x=>x.url),["https://example.net/b"]);
  assert.equal(JSON.stringify(parcel).includes("ignored answer"),false);
});

test("Unsupported provider fails closed",()=>{
  const parcel=aiSourceParcel("other",QUESTION,{});
  assert.equal(parcel.ok,false);
  assert.equal(parcel.source_count,0);
});
