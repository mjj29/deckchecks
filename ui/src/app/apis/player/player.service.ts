import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { IPlayers } from "./player.api";

@Injectable({
        providedIn: 'root'
})
export class PlayerService {

        constructor(private http: HttpClient) { }

        private _url: string = "/rest/player/";

        getPlayer(event: int, namefrag: string): Observable<IPlayers> {
                return this.http.get<IPlayers>("/"+event+this._url+namefrag).pipe(catchError(this.errorHandler));
        }

        errorHandler(error: HttpErrorResponse) {
                return throwError(error.message || "Server Error");
        }
}
