package id.kawalc1.clients

import akka.actor.ActorSystem
import akka.http.scaladsl.model._
import akka.http.scaladsl.model.headers.{Authorization, GenericHttpCredentials}
import akka.http.scaladsl.{ConnectionContext, Http, HttpExt, HttpsConnectionContext}
import akka.stream.Materializer
import akka.util.ByteString
import com.typesafe.scalalogging.LazyLogging
import id.kawalc1.Config.Application
import org.json4s.Formats

import org.json4s.native.Serialization.read

import scala.concurrent.ExecutionContext.Implicits.global
import scala.concurrent.duration.DurationInt
import scala.concurrent.{Await, Future}
import scala.util.{Failure, Success, Try}

case class Response(code: Int, response: String)

trait HttpClientSupport extends LazyLogging {

  def credentialsProvider: Future[Option[Authorization]] = Future.successful(None)

  implicit val system: ActorSystem
  implicit val mat: Materializer
  lazy val http: HttpExt                      = Http()
  def SecurityContext: HttpsConnectionContext = http.defaultClientHttpsContext

  def parseJson[A: Manifest](responseBody: String)(implicit
                                                   mat: Materializer,
                                                   formats: Formats): Either[Response, A] = {
    Try(read[A](responseBody)) match {
      case Success(parsed) => Right(parsed)
      case Failure(ex) =>
        logger.error(s"could not parse response: $ex \n$responseBody")
        Left(Response(500, responseBody))
    }
  }

  def execute[A: Manifest](request: HttpRequest)(implicit
                                                 formats: Formats,
                                                 authorization: Option[Authorization]): Future[Either[Response, A]] = {
    val defaultAuth = headers.Authorization(GenericHttpCredentials("", Application.secret))
    for {
      resp: HttpResponse <- {
        akka.pattern.retry(
          attempt = () => http.singleRequest(request.withHeaders(authorization.toList)),
          attempts = 5,
          delay = 2.seconds,
        )(mat.executionContext, system.scheduler)

      }
      str: String <- consumeEntity(resp.entity)
    } yield {
      resp.status match {
        case code: StatusCode if code.isSuccess() => {
          parseJson[A](str)
        }
        case errorCode =>
          logger.info(s"Request ${request.method.value} ${request.uri}, error: $errorCode")
          logger.info(s"Resp: $str")
          Left(Response(errorCode.intValue(), str))
      }
    }
  }

  private def consumeEntity(entity: HttpEntity)(implicit mat: Materializer): Future[String] =
    entity.toStrict(1.minute).flatMap(_.dataBytes.runFold(ByteString.empty)(_ ++ _).map(_.utf8String))

}
