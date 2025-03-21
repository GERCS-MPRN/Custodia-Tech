package br.mp.mprn.gaeco.custodiatech.repository.auth;

import br.mp.mprn.gaeco.custodiatech.model.auth.Usuario;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.PagingAndSortingRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UsuarioRepository extends PagingAndSortingRepository<Usuario, Long>, JpaSpecificationExecutor<Usuario>, CrudRepository<Usuario, Long> {

    @Query("from Usuario where ativo = true ")
    List<Usuario> listAllAtivo();

    List<Usuario> findUsuarioByUserNameAndDeletadoFalse(@Param("user_name") String user_name);

    Usuario getUsuarioById(@Param("idUsuario") Long idUsuario);

    @Query("select u.nome from Usuario u where u.id = :idUsuario")
    Optional<String> getNomeUsuario(long idUsuario);

    @Query("select u.userName from Usuario u where u.id = :idUsuario")
    Optional<String> getMatriculaUsuario(long idUsuario);

    @Query("select u.codAlfanum from Usuario u where u.id = :idUsuario")
    Optional<String> getCodigoAlfanumerico(long idUsuario);

}
