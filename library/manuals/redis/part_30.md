{"categories":null,"description":"Get started with Redis Open Source","duplicateOf":"head:data-ai-metadata","location":"body","title":"Open Source","tableOfContents":{"sections":[{"id":"use-cases","title":"Use cases"},{"id":"data-integration-tools-libraries-and-frameworks","title":"Data integration tools, libraries, and frameworks"},{"id":"deployment-options","title":"Deployment options"},{"id":"provisioning-and-observability-tools","title":"Provisioning and observability tools"}]},"codeExamples":[]}
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
  2. → [ Open Source ](https://redis.io/docs/latest/get-started/)


#  Open Source 
Get started with Redis Open Source
Redis is an [in-memory data store](https://redis.io/docs/latest/develop/get-started/data-store/) used by millions of developers as a cache, [vector database](https://redis.io/docs/latest/develop/get-started/vector-database/), [document database](https://redis.io/docs/latest/develop/get-started/document-database/), [streaming engine](https://redis.io/docs/latest/develop/data-types/streams/), and message broker. Redis has built-in replication and different levels of [on-disk persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/). It supports complex [data types](https://redis.io/docs/latest/develop/data-types/) (for example, strings, hashes, lists, sets, sorted sets, and JSON), with atomic operations defined on those data types.
Since 2009, the Redis open source project has inspired an enthusiastic and active community of users and contributors. The Redis core source repository is hosted under <https://github.com/redis/redis> along with many of the client libraries. See the [Redis Open Source](https://redis.io/docs/latest/operate/oss_and_stack/) page for more details and links.
You can install Redis from source or from an executable/distribution for your OS.
  * Install Redis on Linux using [APT](https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/apt/), [RPM](https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/rpm/), or [Snap](https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/snap/)
  * [Install Redis on macOS](https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/homebrew/)
  * [Run Redis on Windows using Docker](https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/windows/)
  * [Run Redis on Docker](https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/docker/)
  * [Install Redis from Source](https://redis.io/docs/latest/operate/oss_and_stack/install/build-stack/)
  * [Install Redis with Redis Stack and Redis Insight](https://redis.io/docs/latest/operate/oss_and_stack/install/archive/install-stack/)


##  Use cases [ ](https://redis.io/docs/latest/get-started/#use-cases "Copy link to clipboard")
The following quick start guides will show you how to use Redis for the following specific purposes:
  * [Data structure store](https://redis.io/docs/latest/develop/get-started/data-store/)
  * [Document database](https://redis.io/docs/latest/develop/get-started/document-database/)
  * [Vector database](https://redis.io/docs/latest/develop/get-started/vector-database/)
  * [AI agents and chatbots](https://redis.io/docs/latest/develop/get-started/redis-in-ai/)
  * [Retrieval Augmented Generation (RAG) with Redis](https://redis.io/docs/latest/develop/get-started/rag/)


##  Data integration tools, libraries, and frameworks [ ](https://redis.io/docs/latest/get-started/#data-integration-tools-libraries-and-frameworks "Copy link to clipboard")
  * [Client API libraries](https://redis.io/docs/latest/develop/clients/)
  * [Redis Data Integration](https://redis.io/docs/latest/integrate/redis-data-integration/)
  * [Redis vector library for Python](https://redis.io/docs/latest/develop/ai/redisvl/)
  * [Redis Cloud with Amazon Bedrock](https://redis.io/docs/latest/integrate/amazon-bedrock/)
  * [Object-mapping for .NET](https://redis.io/docs/latest/integrate/redisom-for-net/)
  * [Spring Data Redis for Java](https://redis.io/docs/latest/integrate/spring-framework-cache/)


You can find a complete list of integrations on the [integrations and frameworks hub](https://redis.io/docs/latest/integrate/).
To learn more, refer to the [develop with Redis](https://redis.io/docs/latest/develop/) documentation.
##  Deployment options [ ](https://redis.io/docs/latest/get-started/#deployment-options "Copy link to clipboard")
You can deploy Redis with the following methods:
  * As a service by using [Redis Cloud](https://redis.io/docs/latest/operate/rc/), the fastest way to deploy Redis on your preferred cloud platform.
  * By installing [Redis Enterprise Software](https://redis.io/docs/latest/operate/rs/) in an on-premises data center or on Cloud infrastructure.
  * On a variety Kubernetes distributions by using the [Redis Enterprise operator for Kubernetes](https://redis.io/docs/latest/operate/kubernetes/).


The following guides will help you to get started with your preferred deployment method.
Get started with **[Redis Cloud](https://redis.io/docs/latest/operate/rc/)** by creating a database:
  * The [Redis Cloud quick start](https://redis.io/docs/latest/operate/rc/rc-quickstart/) helps you create a free database. (Start here if you're new.)
  * [Create an Essentials database](https://redis.io/docs/latest/operate/rc/databases/create-database/create-essentials-database/) with a memory limit up to 12 GB.
  * [Create a Pro database](https://redis.io/docs/latest/operate/rc/databases/create-database/create-pro-database-new/) that suits your workload and offers seamless scaling.


Install a **[Redis Enterprise Software](https://redis.io/docs/latest/operate/rs/)** cluster:
  * [Redis Enterprise on Linux quick start](https://redis.io/docs/latest/operate/rs/installing-upgrading/quickstarts/redis-enterprise-software-quickstart/)
  * [Redis Enterprise on Docker quick start](https://redis.io/docs/latest/operate/rs/installing-upgrading/quickstarts/docker-quickstart/)
  * [Get started with Redis Enterprise's Active-Active feature](https://redis.io/docs/latest/operate/rs/databases/active-active/get-started/)
  * [Install and upgrade Redis Enterprise](https://redis.io/docs/latest/operate/rs/installing-upgrading/)


Leverage **[Redis Enterprise for Kubernetes](https://redis.io/docs/latest/operate/kubernetes/)** to simply deploy a Redis Enterprise cluster on Kubernetes:
  * [Deploy Redis Enterprise for Kubernetes](https://redis.io/docs/latest/operate/kubernetes/deployment/quick-start/)
  * [Deploy Redis Enterprise for Kubernetes with OpenShift](https://redis.io/docs/latest/operate/kubernetes/deployment/openshift/)


To learn more, refer to the [Redis products](https://redis.io/docs/latest/operate/) documentation.
##  Provisioning and observability tools [ ](https://redis.io/docs/latest/get-started/#provisioning-and-observability-tools "Copy link to clipboard")
  * [Pulumi provider for Redis Cloud](https://redis.io/docs/latest/integrate/pulumi-provider-for-redis-cloud/)
  * [Terraform provider for Redis Cloud](https://redis.io/docs/latest/integrate/terraform-provider-for-redis-cloud/)
  * [Prometheus and Grafana with Redis Cloud](https://redis.io/docs/latest/integrate/prometheus-with-redis-cloud/)
  * [Prometheus and Grafana with Redis Enterprise](https://redis.io/docs/latest/integrate/prometheus-with-redis-enterprise/)


You can find a complete list of integrations on the [libraries and tools hub](https://redis.io/docs/latest/integrate/).
RATE THIS PAGE
★ ★ ★ ★ ★
[ Back to top ↑ ](https://redis.io/docs/latest/get-started/)
Submit 
[ ](https://github.com/redis/docs/edit/main/content/get-started/_index.md) [ ](https://github.com/redis/docs/issues/new?title=Feedback:%20Open%20Source&body=Page%20https://redis.io/docs/latest/get-started/)
## On this page
  * [Use cases](https://redis.io/docs/latest/get-started/#use-cases)
  * [Data integration tools, libraries, and frameworks](https://redis.io/docs/latest/get-started/#data-integration-tools-libraries-and-frameworks)
  * [Deployment options](https://redis.io/docs/latest/get-started/#deployment-options)
  * [Provisioning and observability tools](https://redis.io/docs/latest/get-started/#provisioning-and-observability-tools)


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
