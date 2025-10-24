package router

import "github.com/gin-gonic/gin"

var engine *gin.Engine

func Init() *gin.Engine {
	engine = gin.Default()
	return engine
}

func Get() *gin.Engine {
	return engine
}
