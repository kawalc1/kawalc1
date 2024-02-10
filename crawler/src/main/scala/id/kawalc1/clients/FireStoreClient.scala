package id.kawalc1.clients
import akka.actor.ActorSystem
import akka.http.scaladsl.client.RequestBuilding.Get
import akka.http.scaladsl.model.headers.{ Authorization, OAuth2BearerToken }
import akka.stream.Materializer
import id.kawalc1.KelurahanOld

import scala.concurrent.{ ExecutionContext, Future }

//
class FireStoreClient(baseUrl: String)(implicit val system: ActorSystem, val mat: Materializer, val ec: ExecutionContext)
  extends HttpClientSupport
  with JsonSupport {

  def getDocId(kelurahan: Int, tps: Int, photo: String, token: String): Future[PhotoCombi] = {
    implicit val authorization = Some(Authorization(OAuth2BearerToken(token)))
    execute[Document](Get(s"$baseUrl$kelurahan-$tps")).map {
      case Right(doc) =>
        println(s"finding $photo ")
        doc.fields.images.mapValue.fields
          .map {
            case (str, set) => PhotoCombi(photo = set.mapValue.fields.url.stringValue, imageId = str)
          }
          .find(_.photo == photo)
          .get
      case Left(resp) => PhotoCombi("wrong", "wrong")
    }

  }
}
