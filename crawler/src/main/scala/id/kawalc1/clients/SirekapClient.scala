package id.kawalc1.clients

import akka.actor.ActorSystem
import akka.http.scaladsl.{Http, HttpExt}
import akka.http.scaladsl.client.RequestBuilding.Get
import akka.http.scaladsl.model.HttpResponse
import akka.http.scaladsl.settings.ConnectionPoolSettings
import akka.stream.Materializer
import akka.stream.scaladsl.Source
import akka.util.ByteString
import com.luciad.imageio.webp.WebPWriteParam
import id.kawalc1.services.FutureHelper

import java.awt.image.BufferedImage
import java.io.{ByteArrayInputStream, File}
import java.net.URI
import java.nio.file.{Files, Paths}
import javax.imageio.stream.FileImageOutputStream
import javax.imageio.{IIOImage, ImageIO, ImageWriteParam}
import scala.concurrent.duration.DurationInt
import scala.concurrent.{ExecutionContext, Future}
import scala.language.postfixOps

case class DprResponse(images: Seq[String])

case class DprPhoto(ord: Int, url: String)
case class DprResult(kelurahan: Long, tps: Int, images: Seq[DprPhoto])

class SirekapClient(baseUrl: String)(implicit
                                     val system: ActorSystem,
                                     val mat: Materializer,
                                     val ec: ExecutionContext)
    extends HttpClientSupport
    with JsonSupport {

  def get(kelurahan: Long, tps: Int): Future[Either[Response, DprResult]] = {
    implicit val authorization = None
    val f                      = s"$kelurahan${"%03d".format(tps)}"
    val path                   = s"${f.substring(0, 2)}/${f.substring(0, 4)}/${f.substring(0, 6)}/$kelurahan/$f.json"
    val url                    = s"$baseUrl/$path"
    execute[DprResponse](Get(url)).map(_.map { x =>
      val images: Seq[DprPhoto] = x.images.filter(_ != null).zipWithIndex.map { case (url, index) => DprPhoto(ord = index, url = url) }
      DprResult(kelurahan, tps, images)
    })
  }

  private def writeImage(imageBytes: BufferedImage, imageSize: Int, image: String, response: DprResult): String = {
    val writer = ImageIO.getImageWritersByMIMEType("image/webp").next

    val writeParam = new WebPWriteParam(writer.getLocale)
    //Notify encoder to consider WebPWriteParams
    writeParam.setCompressionMode(ImageWriteParam.MODE_EXPLICIT)
    val compressionTypes: Array[String] = writeParam.getCompressionTypes
    writeParam.setCompressionType(compressionTypes(WebPWriteParam.LOSSY_COMPRESSION))
    writeParam.setCompressionQuality(0.8f)

    // Save the image
    val imageName = URI.create(image).getPath.split("/").last.replace(".jpg", "")

    val folder = s"dpr/${response.kelurahan}/${response.tps}"
    Files.createDirectories(Paths.get(folder))
    val filePath   = s"$imageName.webp"
    val outputFile = new File(folder, filePath)
    writer.setOutput(new FileImageOutputStream(outputFile))
    writer.write(null, new IIOImage(imageBytes, null, null), writeParam)

    println(s"$image $folder/$filePath ${imageSize / 1024}K -> ${Files.size(outputFile.toPath) / 1024}K")
    filePath
  }
  val orig           = ConnectionPoolSettings(system.settings.config).copy(idleTimeout = 1.minutes)
  val clientSettings = orig.connectionSettings.withIdleTimeout(1.minutes)
  val settings       = orig.copy(connectionSettings = clientSettings)

  private def downloadImage(response: DprResult)(image: DprPhoto): Future[String] = {
    val request = Get(image.url)
    for {
      resp: HttpResponse <- {
        akka.pattern.retry(
          attempt = () => http.singleRequest(request, settings = settings),
          attempts = 5,
          delay = 2.seconds,
        )(mat.executionContext, system.scheduler)
      }
      bytes: ByteString <- {
        resp.entity.withoutSizeLimit().dataBytes.runFold(ByteString.empty) { case (acc, b) => acc ++ b }
      }
    } yield {
      val array                     = bytes.toArray
      val imageBytes: BufferedImage = ImageIO.read(new ByteArrayInputStream(array))
      writeImage(imageBytes, array.length, image.url, response)
    }
  }

  def downloadImages(response: DprResult): Future[DprResult] = {
    FutureHelper.sequence(response.images, downloadImage(response), 8).map(_ => response)
  }

}
