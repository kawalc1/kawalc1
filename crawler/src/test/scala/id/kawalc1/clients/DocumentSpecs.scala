package id.kawalc1.clients
import akka.http.scaladsl.testkit.ScalatestRouteTest
import id.kawalc1.services.BlockingSupport
import org.json4s.native.Serialization
import org.scalatest.{Matchers, WordSpec}

import scala.io.Source

class DocumentSpecs extends WordSpec with Matchers with ScalatestRouteTest with JsonSupport with BlockingSupport {
  "documents" should {
    "parse 1" in {
      val response = Source.fromURL(getClass.getResource("/76-3.json")).mkString
      val document = Serialization.read[Document](response)
      val photos = document.fields.images.mapValue.fields.map {
        case (str, set) => PhotoCombi(str, set.mapValue.fields.url.stringValue)
      }
      photos shouldBe "something"
    }

    "parse 2" in {
      val response = Source.fromURL(getClass.getResource("/80-1.json")).mkString
      val document = Serialization.read[Document](response)
      val photos = document.fields.images.mapValue.fields.map {
        case (str, set) => PhotoCombi(str, set.mapValue.fields.url.stringValue)
      }
      photos shouldBe "something"
    }
  }

}
