package id.kawalc1.services

import akka.http.scaladsl.testkit.ScalatestRouteTest
import id.kawalc1.ProbabilitiesResponse
import id.kawalc1.clients.JsonSupport
import org.json4s.native.Serialization
import org.scalatest.concurrent.ScalaFutures
import org.scalatest.{Matchers, WordSpec}

import scala.io.Source

class PhotoProcessorSpecs extends WordSpec with Matchers with ScalaFutures with ScalatestRouteTest with JsonSupport {
  "PhotoProcessor" should {
    "read probability matrix" in {
      val response      = Source.fromURL(getClass.getResource("/probabilities.json")).mkString
      val probabilities = Serialization.read[ProbabilitiesResponse](response)
      val matrix        = probabilities.probabilityMatrix
      matrix.size shouldBe 2
      matrix.head.size shouldBe 1

      val firstSet = matrix.head.head
      firstSet.confidence shouldBe 0.595609837357855

      val firstNumber = firstSet.numbers.head
      firstNumber.shortName shouldBe "jokowi"
      firstNumber.number shouldBe 102
    }
  }
}
