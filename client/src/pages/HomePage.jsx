import React, { useEffect, useState } from 'react';
import HeroSlide from '../components/common/HeroSlide';
import tmdbConfigs from "../api/configs/tmdb.configs";
import { Box } from '@mui/material';
import uiConfigs from "../configs/ui.configs";
import Container from "../components/common/Container";
import MediaItem from "../components/common/MediaItem";
import predictionApi from '../api/modules/prediction.api';
import nowplayingApi from '../api/modules/nowplaying.api';
import { toast } from "react-toastify";

import { SwiperSlide } from "swiper/react";
import AutoSwiper from "../components/common/AutoSwiper";
import explainApi from '../api/modules/explain.api';
import popularApi from '../api/modules/popular.api';
import topratedApi from '../api/modules/toprated.api';

const HomePage = () => {
  const [predictions, setPredictions] = useState([]);
  const [nowPlaying, setNowPlaying] = useState([]);
  const [popular, setPopular] = useState([]);
  const [toprated, setToprated] = useState([]);
  const [genres, setGenres] = useState([]);

  useEffect(() => {
    const fetchPredictions = async () => {
      const { response, err } = await predictionApi.getList();

      if (response) {
        setPredictions(response);
      } else if (err) {
        console.error("Failed to fetch predictions");
      }
    };

    const fetchNowPlaying = async () => {
      const { response, err } = await nowplayingApi.getList();

      if (response) {
        const randomizedNowPlaying = response.sort(() => Math.random() - 0.5);
        setNowPlaying(randomizedNowPlaying);
      } else if (err) {
        console.error("Failed to fetch now playing movies", err);
      }
    };

    const fetchPopular = async () => {
      const { response, err } = await popularApi.getList();

      if (response) {
        const randomizedPopular = response.sort(() => Math.random() - 0.5);
        setPopular(randomizedPopular);
      } else if (err) {
        console.error("Failed to fetch popular movies", err);
      }
    };

    const fetchToprated = async () => {
      const { response, err } = await topratedApi.getList();

      if (response) {
        const randomizedToprated = response.sort(() => Math.random() - 0.5);
        setToprated(randomizedToprated);
      } else if (err) {
        console.error("Failed to fetch toprated movies", err);
      }
    };

    const fetchExplainList = async () => {
      const { response, err } = await explainApi.getList();

      if (response) {
        const genres = response[0].explains.slice(0, 3);
        setGenres(genres);
      } else if (err) {
        console.error("Failed to fetch explain list", err);
      }
    };

    fetchPredictions();
    fetchNowPlaying();
    fetchPopular();
    fetchToprated();
    fetchExplainList();

    if (!localStorage.getItem("actkn")) {
      toast.info("Signin for Recommendations", {
        position: "top-center",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
    }

  }, []);

  return (
    <>
      <HeroSlide mediaType={tmdbConfigs.mediaType.movie} mediaCategory={tmdbConfigs.mediaCategory.popular} />

      <Box marginTop="-4rem" sx={{ ...uiConfigs.style.mainContent }}>

        {genres.map((genre, i) => {
          const filteredPredictions = predictions.flatMap(prediction => prediction.predictions).filter(media => media.genre_names.includes(genre));
          const randomizedPredictions = filteredPredictions.sort(() => Math.random() - 0.5);
          return (
            randomizedPredictions.length >= 5 && (
              <Container key={i} header={genre}>
                <AutoSwiper>
                  {randomizedPredictions.slice(0, 10).map((media, index) => (
                    <SwiperSlide key={index}>
                      <MediaItem media={media} containerName={genre} />
                    </SwiperSlide>
                  ))}
                </AutoSwiper>
              </Container>
            )
          );
        })}

        {/* {popular.length > 0 && (
          <Container header="Popular">
            <AutoSwiper>
              {popular.map((movie, index) => (
                <SwiperSlide key={index}>
                  <MediaItem media={movie} containerName="Popular" />
                </SwiperSlide>
              ))}
            </AutoSwiper>
          </Container>
        )} */}

        {toprated.length > 0 && (
          <Container header="Top Rated">
            <AutoSwiper>
              {toprated.map((movie, index) => (
                <SwiperSlide key={index}>
                  <MediaItem media={movie} containerName="Top Rated" />
                </SwiperSlide>
              ))}
            </AutoSwiper>
          </Container>
        )}

        {nowPlaying.length > 0 && (
          <Container header="Now Playing">
            <AutoSwiper>
              {nowPlaying.map((movie, index) => (
                <SwiperSlide key={index}>
                  <MediaItem media={movie} containerName="Now Playing" />
                </SwiperSlide>
              ))}
            </AutoSwiper>
          </Container>
        )}

      </Box>
    </>
  );
};

export default HomePage;
