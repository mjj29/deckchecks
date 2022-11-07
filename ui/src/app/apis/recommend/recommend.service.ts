import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { IRecommends } from "./recommend.api";

@Injectable({
        providedIn: 'root'
})
export class RecommendsService {

        constructor(private http: HttpClient) { }

        private _url: string = "/rest/recommend/";

        getRecommends(event: int): Observable<IRecommends> {
                return this.http.get<IRecommends>("/"+event+this._url).pipe(catchError(this.errorHandler));
        }

        errorHandler(error: HttpErrorResponse) {
                return throwError(error.message || "Server Error");
        }
}
