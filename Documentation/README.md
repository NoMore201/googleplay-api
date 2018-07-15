# Documentation

This is a collection of API requests and response for most of the
paths that google play API offers. In general, each requests
usually return the following protobuf objects:

- *payload*: contains the response object
(see `googleplay.proto` for all types of responses).
- (optional) *preFetch*: if the payload contains an URL to be fetched
in order to get results, these results may be pre-fetched by google
servers and included in the original response.

Each requests is discussed in the related subfolder.
