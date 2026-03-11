{"categories":null,"description":"An overview of Redis APIs for developers and operators","duplicateOf":"head:data-ai-metadata","location":"body","title":"APIs","tableOfContents":{"sections":[{"id":"apis-for-developers","title":"APIs for Developers","children":[{"id":"client-api","title":"Client API"},{"id":"programmability-apis","title":"Programmability APIs"}]},{"id":"apis-for-operators","title":"APIs for Operators","children":[{"id":"redis-cloud-api","title":"Redis Cloud API"},{"id":"redis-software-api","title":"Redis Software API"},{"id":"redis-enterprise-for-kubernetes-api","title":"Redis Enterprise for Kubernetes API"}]}]},"codeExamples":[]}
[ ](https://redis.io/)
[Redis for AI](https://redis.io/redis-for-ai/)
Products
##  Products
  * [ Redis Cloud Fully managed and integrated with Google Cloud, Azure, and AWS. ](https://redis.io/cloud/)
  * [ Redis Software Self-managed software with enterprise-grade compliance and reliability. ](https://redis.io/software/)
  * [ Redis Open Source In-memory database for caching & streaming. ](https://redis.io/open-source/)


##  Tools
  * [Redis LangCache](https://redis.io/langcache/)
  * [Redis Insight](https://redis.io/insight/)
  * [Redis Data Integration](https://redis.io/data-integration/)
  * [Clients & Connectors](https://redis.io/clients/)


## Get Redis
[Downloads](https://redis.io/downloads/)
Resources
##  Connect
  * [Customer Stories](https://redis.io/customers/)
  * [Partners](https://redis.io/partners/)
  * [Support](https://redis.io/support/)
  * [Community](https://redis.io/community/)
  * [Events & Webinars](https://redis.io/events/)
  * [Professional Services](https://redis.io/services/professional-services/)


##  Learn
  * [Docs](https://redis.io/docs/)
  * [Commands](https://redis.io/commands/)
  * [Quick starts](https://redis.io/docs/latest/get-started/)
  * [Tutorials](https://redis.io/learn/)
  * [University](https://university.redis.io/)
  * [FAQs](https://redis.io/kb/)
  * [Resources](https://redis.io/resources/)
  * [Blog](https://redis.io/blog/)


##  Latest
  * [Releases](https://redis.io/release/)
  * [News & Updates](https://redis.io/company/news/)


## See how it works
[Visit Demo Center](https://redis.io/demo-center/)
[Docs](https://redis.io/docs/) [Pricing](https://redis.io/pricing/)
[Login](https://cloud.redis.io/) [Book a meeting](https://redis.io/meeting/) [Try Redis](https://redis.io/try-free/) Open search Open main menu
  * [Redis for AI ](https://redis.io/redis-for-ai/)
  * Products
    * [ Redis Cloud Fully managed and integrated with Google Cloud, Azure, and AWS. ](https://redis.io/cloud/)
    * [ Redis Software Self-managed software with enterprise-grade compliance and reliability. ](https://redis.io/software/)
    * [ Redis Open Source In-memory database for caching & streaming. ](https://redis.io/open-source/)
## Tools
    * [Redis LangCache](https://redis.io/langcache/)
    * [Redis Insight](https://redis.io/insight/)
    * [Redis Data Integration](https://redis.io/data-integration/)
    * [Clients & Connectors](https://redis.io/clients/)
## Get Redis
[Downloads](https://redis.io/downloads/)
  * Resources
    * [Customer Stories](https://redis.io/customers/)
    * [Partners](https://redis.io/partners/)
    * [Support](https://redis.io/support/)
    * [Community](https://redis.io/community/)
    * [Events & Webinars](https://redis.io/events/)
    * [Professional Services](https://redis.io/services/professional-services/)
## Learn
    * [Docs](https://redis.io/docs/)
    * [Commands](https://redis.io/commands/)
    * [Quick starts](https://redis.io/docs/latest/get-started/)
    * [Tutorials](https://redis.io/learn/)
    * [University](https://university.redis.io/)
    * [FAQs](https://redis.io/kb/)
    * [Resources](https://redis.io/resources/)
    * [Blog](https://redis.io/blog/)
## Latest
    * [Releases](https://redis.io/release/)
    * [News & Updates](https://redis.io/company/news/)
## See how it works
[Visit Demo Center](https://redis.io/demo-center/)
  * [Docs](https://redis.io/docs/)
  * [Pricing](https://redis.io/pricing/)


  * [Try Redis](https://redis.io/try-free/)
  * [Book a meeting](https://redis.io/meeting/)
  * [ Login ](https://cloud.redis.io/)


[Develop with Redis](https://redis.io/docs/latest/develop) [Libraries and tools](https://redis.io/docs/latest/integrate) [Redis products](https://redis.io/docs/latest/operate)
[Commands](https://redis.io/docs/latest/commands)
  1. [ Docs Docs ](https://redis.io/docs/latest/)
  2. → [ APIs ](https://redis.io/docs/latest/apis/)


#  APIs 
An overview of Redis APIs for developers and operators
Redis provides a number of APIs for developers and operators. The following sections provide you easy access to the client API, the several programmability APIs, the RESTFul management APIs and the Kubernetes resource definitions.
##  APIs for Developers [ ](https://redis.io/docs/latest/apis/#apis-for-developers "Copy link to clipboard")
###  Client API [ ](https://redis.io/docs/latest/apis/#client-api "Copy link to clipboard")
Redis comes with a wide range of commands that help you to develop real-time applications. You can find a complete overview of the Redis commands here:
  * [Redis commands](https://redis.io/docs/latest/commands/)


As a developer, you will likely use one of our supported client libraries for connecting and executing commands.
  * [Connect with Redis clients introduction](https://redis.io/docs/latest/develop/clients/)


###  Programmability APIs [ ](https://redis.io/docs/latest/apis/#programmability-apis "Copy link to clipboard")
The existing Redis commands cover most use cases, but if low latency is a critical requirement, you might need to extend Redis' server-side functionality.
Lua scripts have been available since early versions of Redis. With Lua, the script is provided by the client and cached on the server side, which implies the risk that different clients might use a different script version.
  * [Redis Lua API reference](https://redis.io/docs/latest/develop/programmability/lua-api/)
  * [Scripting with Lua introduction](https://redis.io/docs/latest/develop/programmability/eval-intro/)


The Redis functions feature, which became available in Redis 7, supersedes the use of Lua in prior versions of Redis. The client is still responsible for invoking the execution, but unlike the previous Lua scripts, functions can now be replicated and persisted.
  * [Functions and scripting in Redis 7 and beyond](https://redis.io/docs/latest/develop/programmability/functions-intro/)


If none of the previous methods fulfills your needs, then you can extend the functionality of Redis with new commands using the Redis Modules API.
  * [Redis Modules API introduction](https://redis.io/docs/latest/develop/reference/modules/)
  * [Redis Modules API reference](https://redis.io/docs/latest/develop/reference/modules/modules-api-ref/)


##  APIs for Operators [ ](https://redis.io/docs/latest/apis/#apis-for-operators "Copy link to clipboard")
###  Redis Cloud API [ ](https://redis.io/docs/latest/apis/#redis-cloud-api "Copy link to clipboard")
Redis Cloud is a fully managed Database as a Service offering and the fastest way to deploy Redis at scale. You can programmatically manage your databases, accounts, access, and credentials using the Redis Cloud REST API.
  * [Redis Cloud REST API introduction](https://redis.io/docs/latest/operate/rc/api/)
  * [Redis Cloud REST API examples](https://redis.io/docs/latest/operate/rc/api/examples/)
  * [Redis Cloud REST API reference](https://redis.io/docs/latest/operate/rc/api/api-reference/)


###  Redis Software API [ ](https://redis.io/docs/latest/apis/#redis-software-api "Copy link to clipboard")
If you have installed Redis Software, you can automate operations with the Redis Software REST API.
  * [Redis Software REST API introduction](https://redis.io/docs/latest/operate/rs/references/rest-api/)
  * [Redis Software REST API requests](https://redis.io/docs/latest/operate/rs/references/rest-api/requests/)
  * [Redis Software REST API objects](https://redis.io/docs/latest/operate/rs/references/rest-api/objects/)


###  Redis Enterprise for Kubernetes API [ ](https://redis.io/docs/latest/apis/#redis-enterprise-for-kubernetes-api "Copy link to clipboard")
If you need to install Redis Enterprise on Kubernetes, then you can use the [Redis Enterprise for Kubernetes Operators](https://redis.io/docs/latest/operate/kubernetes/). You can find the resource definitions here:
  * [Redis Enterprise Cluster API](https://redis.io/docs/latest/operate/kubernetes/reference/api/redis_enterprise_cluster_api/)
  * [Redis Enterprise Database API](https://redis.io/docs/latest/operate/kubernetes/reference/api/redis_enterprise_database_api/)


RATE THIS PAGE
★ ★ ★ ★ ★
[ Back to top ↑ ](https://redis.io/docs/latest/apis/)
Submit 
[ ](https://github.com/redis/docs/edit/main/content/apis/_index.md) [ ](https://github.com/redis/docs/issues/new?title=Feedback:%20APIs&body=Page%20https://redis.io/docs/latest/apis/)
## On this page
  * [APIs for Developers](https://redis.io/docs/latest/apis/#apis-for-developers)
    * [Client API](https://redis.io/docs/latest/apis/#client-api)
    * [Programmability APIs](https://redis.io/docs/latest/apis/#programmability-apis)
  * [APIs for Operators](https://redis.io/docs/latest/apis/#apis-for-operators)
    * [Redis Cloud API](https://redis.io/docs/latest/apis/#redis-cloud-api)
    * [Redis Software API](https://redis.io/docs/latest/apis/#redis-software-api)
    * [Redis Enterprise for Kubernetes API](https://redis.io/docs/latest/apis/#redis-enterprise-for-kubernetes-api)


[ ](https://redis.io/)
[ ](https://www.facebook.com/Redisinc) [ ](https://www.youtube.com/c/redisinc) [ ](https://www.linkedin.com/company/redisinc/) [ ](https://www.instagram.com/redisinc/) [ ](https://twitter.com/Redisinc) [ ](https://github.com/redis/)
[Trust](https://trust.redis.io/) [Privacy](https://redis.io/legal/privacy-policy/) [Terms of use](https://redis.io/legal/redis-website-terms-of-use/) [Legal notices](https://redis.io/legal/)
### Use Cases
[Vector database](https://redis.io/solutions/vector-database/) [Feature stores](https://redis.io/solutions/feature-stores/)[Semantic cache](https://redis.io/redis-for-ai/) [Caching](https://redis.io/solutions/caching/)[NoSQL database](https://redis.io/nosql/what-is-nosql/) [Leaderboards](https://redis.io/solutions/leaderboards/) [Data deduplication](https://redis.io/solutions/deduplication/) [Messaging](https://redis.io/solutions/messaging/) [Authentication token storage](https://redis.io/solutions/authentication-token-storage/) [Fast-data ingest](https://redis.io/solutions/fast-data-ingest/) [Query caching](https://redis.io/solutions/query-caching-with-redis-enterprise/) [All solutions](https://redis.io/solutions)
### Industries
[Financial Services](https://redis.io/industries/financial-services/) [Gaming](https://redis.io/industries/gaming/)[Healthcare](https://redis.io/industries/healthcare/) [Retail](https://redis.io/industries/retail/) [All industries](https://redis.io/industries/)
### Compare
[Redis vs Elasticache](https://redis.io/compare/elasticache/) [Redis vs Memcached](https://redis.io/compare/memcached/) [Redis vs Memory Store](https://redis.io/compare/memorystore/) [Redis vs Source Available](https://redis.io/compare/community-edition/)
### Company
[Mission & values](https://redis.io/company/)[Leadership](https://redis.io/company/team/) [Careers](https://redis.io/careers/)[News](https://redis.io/company/news/)
### Connect
[Community](https://redis.io/community/)[Events & webinars](https://redis.io/events/) [News](https://redis.io/company/news/)
### Partners
[Amazon Web Services](https://redis.io/cloud-partners/aws/) [Google Cloud](https://redis.io/cloud-partners/google/) [Microsoft Azure](https://redis.io/cloud-partners/azure/) [All partners](https://redis.io/partners/)
### Support
[Professional services](https://redis.io/services/professional-services/)[Support](https://redis.io/support/)
[Trust](https://trust.redis.io/) [Privacy](https://redis.io/legal/privacy-policy/) [Terms of use](https://redis.io/legal/redis-website-terms-of-use/) [Legal notices](https://redis.io/legal/)
All products Redis Software Redis Cloud Redis Open Source Redis Insight Redis Enterprise for K8s Redis Data Integration Client Libraries ESC 
