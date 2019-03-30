package id.kawalc1

import akka.actor.ActorSystem
import akka.stream.ActorMaterializer
import slick.jdbc.H2Profile.api._

import scala.concurrent.ExecutionContext

object Crawler extends App {

  implicit val system: ActorSystem                = ActorSystem("helloAkkaHttpServer")
  implicit val materializer: ActorMaterializer    = ActorMaterializer()
  implicit val executionContext: ExecutionContext = system.dispatcher

  val db = Database.forConfig("tpsDatabase")
  try {} finally db.close()
}
