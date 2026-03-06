{"categories":["docs","develop","stack","oss","rs","rc","oss","kubernetes","clients"],"description":"Understand how to use Redis for RAG use cases","duplicateOf":"head:data-ai-metadata","location":"body","title":"RAG with Redis","tableOfContents":{"sections":[
* [{"id":"what-is-retrieval-augmented-generation-rag","title":"What is Retrieval Augmented Generation (RAG)?"},{"id":"the-role-of-redis-in-rag","title":"The role of Redis in RAG"},{"id":"build-a-rag-application-with-redis","title":"Build a RAG Application with Redis"},{"id":"benefits-of-using-redis-for-rag","title":"Benefits of Using Redis for RAG"},{"id":"resources","title":"Resources"}]},{"id":"continue-learning-with-redis-university","title":"Continue learning with Redis University"}]},"codeExamples":[]}
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
    * [ Data structure store ](https://redis.io/docs/latest/develop/get-started/data-store/)
    * [ Document database ](https://redis.io/docs/latest/develop/get-started/document-database/)
    * [ Vector database ](https://redis.io/docs/latest/develop/get-started/vector-database/)
    * [ RAG with Redis ](https://redis.io/docs/latest/develop/get-started/rag/)
    * [ GenAI apps ](https://redis.io/docs/latest/develop/get-started/redis-in-ai/)
    * [ FAQ ](https://redis.io/docs/latest/develop/get-started/faq/)
  * [ Client tools ](https://redis.io/docs/latest/develop/tools/)
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
  3. → [ Quick starts ](https://redis.io/docs/latest/develop/get-started/)
  4. → [ RAG with Redis ](https://redis.io/docs/latest/develop/get-started/rag/)


#  RAG with Redis
Understand how to use Redis for RAG use cases
###  What is Retrieval Augmented Generation (RAG)? [ ](https://redis.io/docs/latest/develop/get-started/rag/#what-is-retrieval-augmented-generation-rag "Copy link to clipboard")
Large Language Models (LLMs) generate human-like text but are limited by the data they were trained on. RAG enhances LLMs by integrating them with external, domain-specific data stored in a Redis [vector database](https://redis.io/docs/latest/develop/get-started/vector-database/).
RAG involves three main steps:
  * **Retrieve** : Fetch relevant information from Redis using vector search and filters based on the user query.
  * **Augment** : Create a prompt for the LLM, including the user query, relevant context, and additional instructions.
  * **Generate** : Return the response generated by the LLM to the user.


RAG enables LLMs to use real-time information, improving the accuracy and relevance of generated content. Redis is ideal for RAG due to its speed, versatility, and familiarity.
###  The role of Redis in RAG [ ](https://redis.io/docs/latest/develop/get-started/rag/#the-role-of-redis-in-rag "Copy link to clipboard")
Redis provides a robust platform for managing real-time data. It supports the storage and retrieval of vectors, essential for handling large-scale, unstructured data and performing similarity searches. Key features and components of Redis that make it suitable for RAG include:
  1. **Vector database** : Stores and indexes vector embeddings that semantically represent unstructured data.
  2. **Semantic cache** : Caches frequently asked questions (FAQs) in a RAG pipeline. Using vector search, Redis retrieves similar previously answered questions, reducing LLM inference costs and latency.
  3. **LLM session manager** : Stores conversation history between an LLM and a user. Redis fetches recent and relevant portions of the chat history to provide context, improving the quality and accuracy of responses.
  4. **High performance and scalability** : Known for its [low latency and high throughput](https://redis.io/blog/benchmarking-results-for-vector-databases/), Redis is ideal for RAG systems and AI agents requiring rapid data retrieval and generation.


###  Build a RAG Application with Redis [ ](https://redis.io/docs/latest/develop/get-started/rag/#build-a-rag-application-with-redis "Copy link to clipboard")
To build a RAG application with Redis, follow these general steps:
  1. **Set up Redis** : Start by setting up a Redis instance and configuring it to handle vector data.
  2. **Use a Framework** :
    1. **Redis Vector Library (RedisVL)** : [RedisVL](https://redis.io/docs/latest/integrate/redisvl/) enhances the development of generative AI applications by efficiently managing vectors and metadata. It allows for storage of vector embeddings and facilitates fast similarity searches, crucial for retrieving relevant information in RAG.
    2. **Popular AI frameworks** : Redis integrates seamlessly with various AI frameworks and tools. For instance, combining Redis with [LangChain](https://python.langchain.com/v0.2/docs/integrations/vectorstores/redis/) or [LlamaIndex](https://docs.llamaindex.ai/en/latest/examples/vector_stores/RedisIndexDemo/), libraries for building language models, enables developers to create sophisticated RAG pipelines. These integrations support efficient data management and building real-time LLM chains.
    3. **Spring AI and Redis** : Using [Spring AI with Redis](https://redis.io/blog/building-a-rag-application-with-redis-and-spring-ai/) simplifies building RAG applications. Spring AI provides a structured approach to integrating AI capabilities into applications, while Redis handles data management, ensuring the RAG pipeline is efficient and scalable.
  3. **Embed and store data** : Convert your data into vector embeddings using a suitable model (e.g., BERT, GPT). Store these embeddings in Redis, where they can be quickly retrieved based on vector searches.
  4. **Integrate with a generative model** : Use a generative AI model that can leverage the retrieved data. The model will use the vectors stored in Redis to augment its generation process, ensuring the output is informed by relevant, up-to-date information.
  5. **Query and generate** : Implement the query logic to retrieve relevant vectors from Redis based on the input prompt. Feed these vectors into the generative model to produce augmented outputs.


###  Benefits of Using Redis for RAG [ ](https://redis.io/docs/latest/develop/get-started/rag/#benefits-of-using-redis-for-rag "Copy link to clipboard")
  * **Efficiency** : The in-memory data store of Redis ensures that retrieval operations are performed with minimal latency.
  * **Scalability** : Redis scales horizontally, seamlessly handling growing volumes of data and queries.
  * **Flexibility** : Redis supports a variety of data structures and integrates with AI frameworks.


In summary, Redis offers a powerful and efficient platform for implementing RAG. Its vector management capabilities, high performance, and seamless integration with AI frameworks make it an ideal choice for enhancing generative AI applications with real-time data retrieval.
###  Resources [ ](https://redis.io/docs/latest/develop/get-started/rag/#resources "Copy link to clipboard")
  * [RAG defined](https://redis.io/glossary/retrieval-augmented-generation/).
  * [RAG overview](https://redis.io/kb/doc/2ok7xd1drq/how-to-perform-retrieval-augmented-generation-rag-with-redis).
  * [Redis Vector Library (RedisVL)](https://redis.io/docs/latest/integrate/redisvl/) and [introductory article](https://redis.io/blog/introducing-the-redis-vector-library-for-enhancing-genai-development/).
  * [RAG with Redis and SpringAI](https://redis.io/blog/building-a-rag-application-with-redis-and-spring-ai/)
  * [Build a multimodal RAG app with LangChain and Redis](https://redis.io/blog/explore-the-new-multimodal-rag-template-from-langchain-and-redis/)
  * [Get hands-on with advanced Redis AI Recipes](https://github.com/redis-developer/redis-ai-resources)


##  Continue learning with Redis University [ ](https://redis.io/docs/latest/develop/get-started/rag/#continue-learning-with-redis-university "Copy link to clipboard")
See the [Vector Advanced Topics course](https://university.redis.io/course/i3fv2hbhqnpni8) to learn more.
RATE THIS PAGE
★ ★ ★ ★ ★
[ Back to top ↑ ](https://redis.io/docs/latest/develop/get-started/rag/)
Submit 
[ ](https://github.com/redis/docs/edit/main/content/develop/get-started/rag.md) [ ](https://github.com/redis/docs/issues/new?title=Feedback:%20RAG%20with%20Redis&body=Page%20https://redis.io/docs/latest/develop/get-started/rag)
## On this page
  *     * [What is Retrieval Augmented Generation (RAG)?](https://redis.io/docs/latest/develop/get-started/rag/#what-is-retrieval-augmented-generation-rag)
    * [The role of Redis in RAG](https://redis.io/docs/latest/develop/get-started/rag/#the-role-of-redis-in-rag)
    * [Build a RAG Application with Redis](https://redis.io/docs/latest/develop/get-started/rag/#build-a-rag-application-with-redis)
    * [Benefits of Using Redis for RAG](https://redis.io/docs/latest/develop/get-started/rag/#benefits-of-using-redis-for-rag)
    * [Resources](https://redis.io/docs/latest/develop/get-started/rag/#resources)
  * [Continue learning with Redis University](https://redis.io/docs/latest/develop/get-started/rag/#continue-learning-with-redis-university)


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
