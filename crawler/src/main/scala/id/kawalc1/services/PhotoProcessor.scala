package id.kawalc1.services

import id.kawalc1
import id.kawalc1.SingleTps
import id.kawalc1.clients.{Extraction, JsonSupport, KawalC1Client}
import id.kawalc1.database.{AlignResult, ExtractResult}
import org.json4s.native.Serialization

import scala.concurrent.{ExecutionContext, Future}

case class AlignedPicture(url: String, imageSize: Int)

class PhotoProcessor(client: KawalC1Client)(implicit val ex: ExecutionContext) extends JsonSupport {

  val ImageSize = 1280

  def alignPhoto(tps: Seq[SingleTps]): Future[Seq[Either[String, AlignResult]]] = {
    Future
      .sequence(tps.map { tps: SingleTps =>
        val photo: Array[String] = tps.photo.split("/")
        val photoUrl             = photo(photo.length - 1)
        val formType             = tps.verification.c1.get.`type`
        val formConfig           = kawalc1.formTypeToConfig(formType)
        client.alignPhoto(tps.kelurahanId, tps.tpsId, photoUrl, ImageSize, formConfig).map {
          case Right(t) =>
            t.transformedUrl match {
              case Some(trans) =>
                Right(
                  AlignResult(tps.kelurahanId,
                              tps.tpsId,
                              tps.photo,
                              ImageSize,
                              100,
                              formConfig,
                              Some(trans),
                              None))
              case None =>
                Right(
                  AlignResult(tps.kelurahanId,
                              tps.tpsId,
                              tps.photo,
                              ImageSize,
                              0,
                              formConfig,
                              None,
                              None))
            }
          case Left(str) => Left(str)
        }
      })
  }

  def extractNumbers(results: Seq[AlignResult]): Future[Seq[Either[String, ExtractResult]]] = {
    Future
      .sequence(results.map { res: AlignResult =>
        for {
          extracted <- client.extractNumbers(res.id, res.tps, res.photo, res.config)
        } yield {
          extracted match {
            case Right(e: Extraction) =>
              Right(
                ExtractResult(res.id, res.tps, res.photo, Serialization.write(e), e.digitArea, ""))
            case Left(str) => Left(str)
          }
        }
      })

  }
}
