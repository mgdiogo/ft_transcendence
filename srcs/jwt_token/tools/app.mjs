import Fastify from 'fastify/fastify.js'
const fastify = Fastify({
	logger: true
})

const listeners = ['SIGINT', 'SIGTERM']
listeners.forEach((signal) => {
	process.on(signal, async () => {
		await fastify.close()
		process.exit(0)
	})
})

fastify.get('/healthcheck', async function handler(request, reply) {
	return { message: 'success' }
})

try {
	await fastify.listen({ port: 3000, host: '0.0.0.0' })
} catch (err) {
	fastify.log.error(err)
	process.exit(1)
}