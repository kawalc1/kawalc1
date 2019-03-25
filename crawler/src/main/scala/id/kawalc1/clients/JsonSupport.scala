package id.kawalc1.clients

import java.sql.Timestamp
import java.time.Instant

import com.typesafe.scalalogging.LazyLogging
import de.heikoseeberger.akkahttpjson4s.Json4sSupport
import enumeratum.values.{IntEnumEntry, ShortEnumEntry}
import org.json4s.JsonAST.{JInt, JLong, JObject}
import org.json4s.native.Serialization
import org.json4s.{CustomSerializer, DefaultFormats, Formats, native}
import enumeratum.values._

import scala.collection.immutable


case class C1(
  plano: Plano,
  `type`: FormType
)

case class Verification(
  ts: Timestamp,
  c1: Option[C1],
  sum: Option[Summary]
)


case class Tps(
  photos: Map[String, Verification])

case class Kelurahan(
  id: Int,
  name: String,
  parentNames: Seq[String],
  data: Map[Int, Tps]
)

trait Summary

case class PresidentialLembar1(
  jum: Int,
  plano: Boolean
) extends Summary


case class PresidentialLembar2(
  pas1: Int,
  pas2: Int,
  sah: Int,
  tSah: Int,
) extends Summary


case class SingleSum(
  jum: Int,
) extends Summary

case class Dpr(
  votes: Map[String, Int],
) extends Summary


sealed abstract class Plano(val value: Short) extends ShortEnumEntry

case object Plano extends ShortEnum[Plano] {

  case object YES extends Plano(1)

  case object NO extends Plano(2)

  val values: immutable.IndexedSeq[Plano] = findValues
}

sealed abstract class FormType(val value: Short) extends ShortEnumEntry

case object FormType extends ShortEnum[FormType] {

  // Full blown until digitized.
  case object PPWP extends FormType(1)

  case object DPR extends FormType(2)

  // Only up to halaman, not digitized.
  case object DPD extends FormType(3)

  case object DPRP extends FormType(4)

  case object DPRPB extends FormType(5)

  case object DPRA extends FormType(6)

  case object DPRD_PROV extends FormType(7)

  case object DPRD_KAB_KOTA extends FormType(8)

  case object DPRK extends FormType(9)

  // Up to choosing this type.
  case object OTHERS extends FormType(10)

  case object DELETED extends FormType(11)

  case object MALICIOUS extends FormType(12)

  val values: immutable.IndexedSeq[FormType] = findValues
}

trait JsonSupport extends Json4sSupport with LazyLogging {
  implicit val serialization: Serialization.type = native.Serialization

  private def parseSummary(c1: C1, summary: JObject): Option[Summary] = {
    c1 match {
      case C1(Plano.YES, FormType.PPWP) => Some(summary.extract[PresidentialLembar2])
      case C1(Plano.YES, FormType.DPR) => Some(summary.extract[Dpr])
      case _ => None
    }
  }

  case object SummarySerialize extends CustomSerializer[Verification](format => ( {
    case JObject(List(("c1", c1Json: JObject), ("sum", sum: JObject), ("ts", JInt(tss)))) =>
      val timeStamp = Timestamp.from(Instant.ofEpochMilli(tss.toLong))
      val c1 = c1Json.extract[C1]
      val summary = sum match {
        case JObject(List(("jum", JInt(num)))) => Some(SingleSum(num.toInt))
        case x: JObject => parseSummary(c1, sum)
      }

      Verification(timeStamp, Some(c1), summary)
  }, {
    case x: Verification => throw new Exception("cannot serialize")
  }
  )
  )

  import org.json4s.DefaultFormats

  val standardFormats: Formats = DefaultFormats + SummarySerialize ++ Seq(Json4s.serializer(FormType), Json4s.serializer(Plano))

  implicit val formats: Formats = standardFormats
}
