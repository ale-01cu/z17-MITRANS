export const getValidationErrors = (errors: any) => {
	const validationErrors = errors.reduce((acc: any, error: any) => {
		const field = error.path.join('.') // Obtener el campo (field)
		acc[field] = error.message // Asignar el mensaje de error al campo
		return acc
	}, {})
	return validationErrors
}