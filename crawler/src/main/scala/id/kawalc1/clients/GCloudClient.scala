package id.kawalc1.clients
import java.nio.file.Paths

import akka.actor.ActorSystem
import akka.http.scaladsl.client.RequestBuilding.Get
import akka.http.scaladsl.model.Uri
import akka.stream.Materializer
import akka.stream.scaladsl.FileIO

import scala.concurrent.{ ExecutionContext, Future }

class GCloudClient(implicit
  val system: ActorSystem,
  val mat: Materializer,
  val ec: ExecutionContext)
  extends HttpClientSupport
  with JsonSupport {

  def getImage(kelurahan: Int, tps: Int, photo: String) = {
    implicit val authorization = None
    val baseUrl = "https://storage.googleapis.com/kawalc1/static/transformed/"
    val photoFile = Paths.get(s"$kelurahan-$tps-$photo.webp")
    val url = Uri(s"$baseUrl/$kelurahan/$kelurahan/$tps/extracted/$photo%3Ds1280~digit-area.webp")
    download(Get(url)).flatMap(_.runWith(FileIO.toPath(photoFile)))
  }

}
