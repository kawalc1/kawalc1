package id.kawalc1

import java.util.concurrent.TimeUnit

import scala.concurrent.{Await, Future}
import scala.concurrent.duration.Duration
import scala.language.implicitConversions

trait FutureMatcher {

  implicit def fh[T](f: Future[T]): Object {
    def futureValue: T
  } = new {
    def futureValue: T = Await.result(f, Duration(300, TimeUnit.SECONDS))
  }

}
