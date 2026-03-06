{"categories":null,"description":"Tools to interact with a Redis server","duplicateOf":"head:data-ai-metadata","location":"body","title":"Client tools","tableOfContents":{"sections":[{"id":"redis-command-line-interface-cli","title":"Redis command line interface (CLI)"},{"id":"redis-insight","title":"Redis Insight"},{"id":"redis-vscode-extension","title":"Redis VSCode extension"}]},"codeExamples":[]}
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


[Develop with Redis](https://redis.io/docs/latest/develop)
  * [ What's new? ](https://redis.io/docs/latest/develop/whats-new/)
  * [ Quick starts ](https://redis.io/docs/latest/develop/get-started/)
  * [ Client tools ](https://redis.io/docs/latest/develop/tools/)
    * [ CLI ](https://redis.io/docs/latest/develop/tools/cli/)
    * [ Redis Insight ](https://redis.io/docs/latest/develop/tools/insight/)
    * [ Redis for VS Code ](https://redis.io/docs/latest/develop/tools/redis-for-vscode/)
  * [ Client APIs ](https://redis.io/docs/latest/develop/clients/)
  * [ Using commands ](https://redis.io/docs/latest/develop/using-commands/)
  * [ Data types ](https://redis.io/docs/latest/develop/data-types/)
  * [ Redis for AI and search ](https://redis.io/docs/latest/develop/ai/)
  * [ Programmability ](https://redis.io/docs/latest/develop/programmability/)
  * [ Pub/sub ](https://redis.io/docs/latest/develop/pubsub/)
  * [ Reference ](https://redis.io/docs/latest/develop/reference/)

[Libraries and tools](https://redis.io/docs/latest/integrate) [Redis products](https://redis.io/docs/latest/operate)
[Commands](https://redis.io/docs/latest/commands)
  1. [ Docs Docs ](https://redis.io/docs/latest/)
  2. → [ Develop with Redis ](https://redis.io/docs/latest/develop/)
  3. → [ Client tools ](https://redis.io/docs/latest/develop/tools/)


#  Client tools 
Tools to interact with a Redis server
You can use several tools to connect to a Redis server, to manage it and interact with the data:
  * The [`redis-cli`](https://redis.io/docs/latest/develop/tools/#redis-command-line-interface-cli) command line tool
  * [Redis Insight](https://redis.io/docs/latest/develop/tools/#redis-insight) (a graphical user interface tool)
  * The Redis [VSCode extension](https://redis.io/docs/latest/develop/tools/#redis-vscode-extension)


##  Redis command line interface (CLI) [ ](https://redis.io/docs/latest/develop/tools/#redis-command-line-interface-cli "Copy link to clipboard")
The [Redis command line interface](https://redis.io/docs/latest/develop/tools/cli/) (also known as `redis-cli`) is a terminal program that sends commands to and reads replies from the Redis server. It has the following two main modes:
  1. An interactive Read Eval Print Loop (REPL) mode where the user types Redis commands and receives replies.
  2. A command mode where `redis-cli` is executed with additional arguments, and the reply is printed to the standard output.


##  Redis Insight [ ](https://redis.io/docs/latest/develop/tools/#redis-insight "Copy link to clipboard")
[Redis Insight](https://redis.io/docs/latest/develop/tools/insight/) combines a graphical user interface with Redis CLI to let you work with any Redis deployment. You can visually browse and interact with data, take advantage of diagnostic tools, learn by example, and much more. Best of all, Redis Insight is free.
[Download Redis Insight](https://redis.io/downloads/#insight).
##  Redis VSCode extension [ ](https://redis.io/docs/latest/develop/tools/#redis-vscode-extension "Copy link to clipboard")
[Redis for VS Code](https://redis.io/docs/latest/develop/tools/redis-for-vscode/) is an extension that allows you to connect to your Redis databases from within Microsoft Visual Studio Code. After connecting to a database, you can view, add, modify, and delete keys, and interact with your Redis databases using a Redis Insight like UI and also a built-in CLI interface.
RATE THIS PAGE
★ ★ ★ ★ ★
[ Back to top ↑ ](https://redis.io/docs/latest/develop/tools/)
Submit 
[ ](https://github.com/redis/docs/edit/main/content/develop/tools/_index.md) [ ](https://github.com/redis/docs/issues/new?title=Feedback:%20Client%20tools&body=Page%20https://redis.io/docs/latest/develop/tools/)
## On this page
  * [Redis command line interface (CLI)](https://redis.io/docs/latest/develop/tools/#redis-command-line-interface-cli)
  * [Redis Insight](https://redis.io/docs/latest/develop/tools/#redis-insight)
  * [Redis VSCode extension](https://redis.io/docs/latest/develop/tools/#redis-vscode-extension)


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
