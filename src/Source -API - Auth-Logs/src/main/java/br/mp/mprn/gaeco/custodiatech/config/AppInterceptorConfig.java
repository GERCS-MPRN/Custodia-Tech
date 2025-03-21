package br.mp.mprn.gaeco.custodiatech.config;


import br.mp.mprn.gaeco.custodiatech.interceptors.AuthInterceptor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class AppInterceptorConfig implements WebMvcConfigurer {

    @Value("${custodiatech-api.jwt.secret}")
    private String jwtSecret;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new AuthInterceptor(jwtSecret));
    }
}
