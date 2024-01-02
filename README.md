### 🎬 About The Project

This project involves the development of a personalized recommendation system for a movie streaming service.

Website: [https://kawastream.kawamottyan.com/](https://kawastream.kawamottyan.com/)

This project inspired by  
- [Netflix Technology Blog](https://netflixtechblog.medium.com/)
- [hungpthanh's GitHub Project](https://github.com/hungpthanh/GRU4REC-pytorch)
- [trananhtuat's GitHub Project](https://github.com/trananhtuat/fullstack-mern-movie-2022)
- [@DataScienceGarage's Youtube Tutorial](https://www.youtube.com/watch?v=stD47vPDadI)

### 👏 Getting Started

1. Setup

    clone my repo
    ```
    git clone https://github.com/kawamottyan/kawastream.git
    ```

    change directory
    ```
    cd kawastream
    ```


2. Server deployment

    create env file in the server folder
    ```
    MONGODB_URL=mongodb+srv://... # add your MongoDB Connection String here
    PORT=5000
    TOKEN_SECRET=... # create your secret key here
    TMDB_BASE_URL=https://api.themoviedb.org/3/
    TMDB_KEY=eec... # add your TMDB API key here
    ```

    run server
    ```
    cd server
    yarn install
    yarn start
    ```

3. Client deployment

    run client
    ```
    cd client
    yarn install
    yarn start
    ```

4. Model deployment

    set up data from MovieLens
    - run dataprocessing.ipynb
    - run datasplitting.ipynb

    set up aws
    - save data from datasplitting.ipynb in s3
    - set up sagemaker
    - set up lambda

### 🗂️ Structure

```
├─ client
│   ├─ public
│   └─ src
│       ├─ api
│       │   ├─ client
│       │   ├─ configs
│       │   └─ modules
│       ├─ components
│       ├─ configs
│       ├─ hooks
│       ├─ pages
│       ├─ redux
│       ├─ routes
│       ├─ util
│       ├─ App.jsx
│       └─ index.jsx
├─ model
│   ├─ eval
│   ├─ experiment
│   │   ├─ EDA
│   │   └─ model
│   │       ├─ benchmark
│   │       ├─ reinforcement_learning
│   │       └─ rnn
│   ├─ dataprocessing.ipynb
│   └─ datasplitting.ipynb
├─ server
│   ├─ src
│   │   ├─ axios
│   │   ├─ controllers
│   │   ├─ handlers
│   │   ├─ middlewares
│   │   ├─ models
│   │   ├─ routes
│   │   └─ tmdb
│   ├─ .env.example
│   └─ index.js
├─ LICENSE
└─ README.md
```
### 🚗 Roadmap

- [ ] Verification in an Online Environment


### 📌 License

Apache-2.0 license

### 👤 Contact

Name: Masato Kawamoto  
Email: kawamoto@kawamottyan.com
