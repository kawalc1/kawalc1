package id.kawalc1.clients

import java.sql.Timestamp
import java.time.Instant

import com.typesafe.scalalogging.LazyLogging
import de.heikoseeberger.akkahttpjson4s.Json4sSupport
import enumeratum.values._
import id.kawalc1._
import org.json4s.JsonAST.{ JInt, JObject }
import org.json4s.native.Serialization
import org.json4s.{ CustomSerializer, Formats, native }
import org.json4s._

trait JsonSupport extends Json4sSupport with LazyLogging {
  implicit val serialization: Serialization.type = native.Serialization

  private def parseSummary(c1: Option[C1], summary: JObject): Option[Summary] = {
    c1 match {
      case Some(C1(Some(_), FormType.PPWP, Some("2"))) => Some(summary.extract[PresidentialLembar2])
      case Some(C1(Some(Plano.YES), FormType.DPR, _)) =>
        val map = summary.extract[Map[String, Int]].head
        Some(Dpr(map._1, map._2))
      case None => Some(summary.extract[Pending])
      case _ => None
    }
  }

  case object SummarySerialize
    extends CustomSerializer[Verification](format =>
      ({
        case x: JObject =>
          val tss = (x \ "ts").extract[Long]
          val maybeC1 = (x \ "c1").extract[Option[C1]]
          val sum = (x \ "sum").extract[JObject]
          val timeStamp = Timestamp.from(Instant.ofEpochMilli(tss))

          val jum = (sum \ "jum").extract[Option[Int]]
          val pJum = (sum \ "pJum").extract[Option[Int]]

          val cakupan = (sum \ "cakupan").extract[Option[Int]]
          val pending = (sum \ "pending").extract[Option[Int]]
          val error = (sum \ "error").extract[Option[Int]]
          val janggal = (sum \ "janggal").extract[Option[Int]]

          val common = Common(cakupan, pending, error, janggal)

          val summary = (jum, pJum) match {
            case (Some(num), None) => Some(SingleSum(num))
            case (None, Some(num)) => Some(LegislativeSum(num))
            case _ => parseSummary(maybeC1, sum)
          }

          Verification(timeStamp, maybeC1, summary, common)
      }, {
        case _: Verification => throw new Exception("cannot serialize")
      }))

  import org.json4s.DefaultFormats

  val standardFormats: Formats = DefaultFormats + SummarySerialize ++ Seq(Json4s.serializer(FormType), Json4s.serializer(Plano))

  implicit val formats: Formats = standardFormats
}
