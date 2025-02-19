// * This code is from https://fastify.dev being currently used for testing purposes

// Import the framework and instantiate it
import Fastify from 'fastify/fastify.js'
const fastify = Fastify({
	logger: true
})

// Declare a route
fastify.get('/', async function handler(request, reply) {
	return { hello: 'world' }
})

// Run the server!
try {
	await fastify.listen({ port: 3000 })
} catch (err) {
	fastify.log.error(err)
	process.exit(1)
}