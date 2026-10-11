package id.kawalc1.images
import com.luciad.imageio.webp.WebPWriteParam
import org.scalatest.{Matchers, WordSpec}

import java.awt.image.BufferedImage
import java.io.File
import javax.imageio.stream.{FileImageOutputStream, ImageInputStream}
import javax.imageio.{IIOImage, ImageIO, ImageWriteParam}
import scala.io.Source

class ConvertSpecs extends WordSpec with Matchers {
  "webp conversion" should {
    "work for jpg" in {
      val image: BufferedImage = ImageIO.read(getClass.getResource("/images/1.jpg"))
      val writer               = ImageIO.getImageWritersByMIMEType("image/webp").next

      val writeParam = new WebPWriteParam(writer.getLocale)
      //Notify encoder to consider WebPWriteParams
      writeParam.setCompressionMode(ImageWriteParam.MODE_EXPLICIT)
      val compressionTypes: Array[String] = writeParam.getCompressionTypes
      writeParam.setCompressionType(compressionTypes(WebPWriteParam.LOSSY_COMPRESSION))
      writeParam.setCompressionQuality(0.8f)

      // Save the image
      writer.setOutput(new FileImageOutputStream(new File("sample.webp")))
      writer.write(null, new IIOImage(image, null, null), writeParam)
    }
  }
}
